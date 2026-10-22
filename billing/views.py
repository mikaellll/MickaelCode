import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from courses.models import Course
from .models import Order
from .services import StripeBillingService


@login_required
@require_POST
def create_checkout_session_view(request, course_slug):
    """
    Initiates Stripe Checkout session for authenticated student.
    """
    course = get_object_or_404(Course, slug=course_slug, status="published")

    # If user is already enrolled
    if course.user_is_enrolled(request.user):
        messages.info(request, "Vous possédez déjà cette formation.")
        return redirect("courses:course_detail", slug=course.slug)

    try:
        session_data = StripeBillingService.create_checkout_session(
            user=request.user,
            course=course,
            request=request
        )
        return redirect(session_data["url"])
    except Exception as e:
        messages.error(request, f"Impossible d'initialiser le paiement Stripe : {e}")
        return redirect("courses:course_detail", slug=course.slug)


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    """
    Stripe Webhook Endpoint. Verifies HMAC signature and processes order fulfillment idempotently.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    success, message = StripeBillingService.handle_webhook_event(payload, sig_header)

    if success:
        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest(message)


def payment_success_view(request):
    """
    Displayed after returning from Stripe Checkout.
    Reminder: Course is unlocked by the verified webhook, not just landing here.
    """
    session_id = request.GET.get("session_id", "")
    is_simulated = request.GET.get("simulated", "") == "true"

    order = None
    if session_id:
        order = Order.objects.filter(stripe_checkout_session_id=session_id).first()

    # For development ease when testing locally without live Stripe webhooks:
    if is_simulated and order and request.user.is_authenticated and order.user == request.user:
        if order.status == "pending":
            # Simulate webhook execution for dev environment
            mock_payload = json.dumps({
                "id": f"evt_simulated_{order.order_reference}",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": session_id,
                        "client_reference_id": order.order_reference,
                        "payment_intent": f"pi_mock_{order.order_reference}",
                        "metadata": {"order_reference": order.order_reference}
                    }
                }
            })
            StripeBillingService.handle_webhook_event(mock_payload, "simulated_sig")
            order.refresh_from_db()

    return render(request, "billing/success.html", {
        "order": order,
        "is_simulated": is_simulated,
    })


def payment_cancel_view(request):
    """
    Displayed when student cancels during Stripe Checkout.
    """
    course_slug = request.GET.get("course_slug", "")
    course = None
    if course_slug:
        course = Course.objects.filter(slug=course_slug).first()

    return render(request, "billing/cancel.html", {
        "course": course
    })
