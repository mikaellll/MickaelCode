import json
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from courses.models import Course, Enrollment
from billing.models import Order, PaymentWebhookEvent
from billing.services import StripeBillingService

User = get_user_model()


class BillingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student_test",
            email="student_test@example.com",
            password="password123"
        )
        self.course = Course.objects.create(
            title="Formation Stripe Test",
            slug="formation-stripe-test",
            short_description="Short",
            description_markdown="Long",
            price=Decimal("49.00"),
            currency="EUR",
            status="published"
        )

    def test_create_checkout_session(self):
        self.client.force_login(self.user)
        url = reverse("billing:create_checkout_session", kwargs={"course_slug": self.course.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        order = Order.objects.filter(user=self.user, course=self.course).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.amount, Decimal("49.00"))

    def test_webhook_successful_checkout_unlocks_enrollment(self):
        order = Order.objects.create(
            user=self.user,
            course=self.course,
            amount=self.course.price,
            currency="EUR",
            status="pending",
            stripe_checkout_session_id="cs_test_session_123"
        )

        payload = json.dumps({
            "id": "evt_test_12345",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session_123",
                    "client_reference_id": order.order_reference,
                    "payment_intent": "pi_test_12345",
                    "metadata": {"order_reference": order.order_reference}
                }
            }
        })

        success, msg = StripeBillingService.handle_webhook_event(payload, "sig")
        self.assertTrue(success)

        order.refresh_from_db()
        self.assertEqual(order.status, "completed")

        enrollment = Enrollment.objects.filter(user=self.user, course=self.course, status="active").first()
        self.assertIsNotNone(enrollment)

    def test_webhook_idempotency(self):
        order = Order.objects.create(
            user=self.user,
            course=self.course,
            amount=self.course.price,
            currency="EUR",
            status="pending",
            stripe_checkout_session_id="cs_test_session_repeat"
        )

        payload = json.dumps({
            "id": "evt_test_repeat_001",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session_repeat",
                    "client_reference_id": order.order_reference,
                    "payment_intent": "pi_test_repeat",
                    "metadata": {"order_reference": order.order_reference}
                }
            }
        })

        # First call
        success1, _ = StripeBillingService.handle_webhook_event(payload, "sig")
        self.assertTrue(success1)
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

        # Second delivery of identical webhook
        success2, msg2 = StripeBillingService.handle_webhook_event(payload, "sig")
        self.assertTrue(success2)
        self.assertEqual(msg2, "Already processed")
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_webhook_refund_revokes_access(self):
        order = Order.objects.create(
            user=self.user,
            course=self.course,
            amount=self.course.price,
            currency="EUR",
            status="completed",
            stripe_payment_intent_id="pi_to_refund"
        )
        Enrollment.objects.create(user=self.user, course=self.course, status="active")

        payload = json.dumps({
            "id": "evt_test_refund_001",
            "type": "charge.refunded",
            "data": {
                "object": {
                    "payment_intent": "pi_to_refund"
                }
            }
        })

        success, _ = StripeBillingService.handle_webhook_event(payload, "sig")
        self.assertTrue(success)

        order.refresh_from_db()
        self.assertEqual(order.status, "refunded")

        enrollment = Enrollment.objects.get(user=self.user, course=self.course)
        self.assertEqual(enrollment.status, "revoked")
