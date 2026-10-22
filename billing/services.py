import logging
import stripe
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from courses.models import Course, Enrollment
from dashboard.models import StudentNotification
from .models import Order, PaymentWebhookEvent

logger = logging.getLogger(__name__)


class StripeBillingService:
    @staticmethod
    def get_stripe_client():
        stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")
        return stripe

    @classmethod
    def create_checkout_session(cls, user, course, request):
        """
        Creates a Stripe Checkout Session for the given course and user.
        Always relies on the database price (never trust browser).
        """
        cls.get_stripe_client()
        site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000").rstrip("/")

        success_url = f"{site_url}{reverse('billing:payment_success')}?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{site_url}{reverse('billing:payment_cancel')}?course_slug={course.slug}"

        # Create or update pending order in database
        order = Order.objects.create(
            user=user,
            course=course,
            amount=course.price,
            currency=course.currency,
            status="pending"
        )

        # Check if Stripe keys are configured
        stripe_key = getattr(settings, "STRIPE_SECRET_KEY", "")
        if not stripe_key or stripe_key.startswith("sk_test_placeholder") or "sample" in stripe_key:
            # Development fallback: generate a simulated session ID
            simulated_session_id = f"cs_test_mock_{order.order_reference}"
            order.stripe_checkout_session_id = simulated_session_id
            order.save(update_fields=["stripe_checkout_session_id"])
            return {
                "id": simulated_session_id,
                "url": f"{reverse('billing:payment_success')}?session_id={simulated_session_id}&simulated=true",
                "order": order
            }

        # Real Stripe API Call
        line_items = [
            {
                "price_data": {
                    "currency": course.currency.lower(),
                    "unit_amount": int(course.price * 100), # amount in cents
                    "product_data": {
                        "name": course.title,
                        "description": course.short_description[:250],
                    },
                },
                "quantity": 1,
            }
        ]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            customer_email=user.email,
            client_reference_id=order.order_reference,
            line_items=line_items,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_reference": order.order_reference,
                "user_id": str(user.id),
                "course_id": str(course.id),
                "course_slug": course.slug,
            }
        )

        order.stripe_checkout_session_id = session.id
        order.save(update_fields=["stripe_checkout_session_id"])

        return {
            "id": session.id,
            "url": session.url,
            "order": order
        }

    @classmethod
    def handle_webhook_event(cls, payload, sig_header):
        """
        Idempotently verifies and processes Stripe webhooks.
        """
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        cls.get_stripe_client()

        # In dev/mock testing without webhook signature
        if not webhook_secret or webhook_secret.startswith("whsec_placeholder") or "sample" in webhook_secret:
            import json
            try:
                event_data = json.loads(payload)
                event_id = event_data.get("id", "evt_mock_000")
                event_type = event_data.get("type", "checkout.session.completed")
                event = event_data
            except Exception as e:
                return False, f"Invalid JSON payload: {e}"
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
                event_id = event["id"]
                event_type = event["type"]
            except Exception as e:
                logger.error(f"Stripe Webhook Signature Verification Failed: {e}")
                return False, str(e)

        # Idempotency check: verify if event was already processed
        webhook_record, created = PaymentWebhookEvent.objects.get_or_create(
            stripe_event_id=event_id,
            defaults={
                "event_type": event_type,
                "payload": event if isinstance(event, dict) else event.to_dict_recursive(),
                "processed": False
            }
        )

        if not created and webhook_record.processed:
            logger.info(f"Stripe Webhook event {event_id} was already processed. Skipping.")
            return True, "Already processed"

        # Dispatch event processing
        try:
            with transaction.atomic():
                if event_type == "checkout.session.completed":
                    session_obj = event["data"]["object"]
                    cls._process_successful_checkout(session_obj)

                elif event_type == "charge.refunded":
                    charge_obj = event["data"]["object"]
                    cls._process_refund(charge_obj)

                webhook_record.processed = True
                webhook_record.save(update_fields=["processed"])

            return True, "Processed successfully"

        except Exception as e:
            logger.exception(f"Error handling webhook event {event_id}: {e}")
            webhook_record.error_message = str(e)
            webhook_record.save(update_fields=["error_message"])
            return False, str(e)

    @classmethod
    def _process_successful_checkout(cls, session):
        """
        Fulfills order and unlocks course access for student.
        """
        session_id = session.get("id")
        order_ref = session.get("client_reference_id") or session.get("metadata", {}).get("order_reference")

        order = None
        if order_ref:
            order = Order.objects.filter(order_reference=order_ref).first()
        if not order and session_id:
            order = Order.objects.filter(stripe_checkout_session_id=session_id).first()

        if not order:
            logger.error(f"Cannot fulfill order: No matching Order found for session {session_id} / ref {order_ref}")
            return

        order.status = "completed"
        order.stripe_payment_intent_id = session.get("payment_intent") or ""
        order.save(update_fields=["status", "stripe_payment_intent_id", "updated_at"])

        # Unlock course enrollment for user
        enrollment, _ = Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={
                "status": "active",
                "acquisition_source": "stripe",
                "stripe_session_id": session_id or "",
            }
        )
        if enrollment.status != "active":
            enrollment.status = "active"
            enrollment.save(update_fields=["status"])

        # Notify student in their dashboard
        StudentNotification.objects.create(
            user=order.user,
            title=f"Accès débloqué : {order.course.title}",
            message=f"Votre commande {order.order_reference} a été confirmée. Vous pouvez dès à présent visionner l'ensemble des leçons de la formation.",
            link=f"/courses/{order.course.slug}/"
        )
        logger.info(f"Enrollment confirmed for user {order.user.email} in {order.course.title}")

    @classmethod
    def _process_refund(cls, charge):
        """
        Handles refund: updates order status and revokes course access.
        """
        payment_intent = charge.get("payment_intent")
        if payment_intent:
            order = Order.objects.filter(stripe_payment_intent_id=payment_intent).first()
            if order:
                order.status = "refunded"
                order.save(update_fields=["status", "updated_at"])

                # Revoke enrollment
                Enrollment.objects.filter(user=order.user, course=order.course).update(status="revoked")

                StudentNotification.objects.create(
                    user=order.user,
                    title="Remboursement de formation",
                    message=f"Le remboursement de votre commande {order.order_reference} a été effectué. L'accès à la formation a été révoqué.",
                    link="/dashboard/purchases/"
                )
