from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import NewsletterSubscriber
from .services import get_newsletter_service


@require_POST
def subscribe_view(request):
    """
    Voluntary GDPR-compliant newsletter subscription.
    """
    email = request.POST.get("email", "").strip().lower()
    consent = request.POST.get("consent") == "on" or request.POST.get("consent") is True

    if not email:
        messages.error(request, "Veuillez renseigner une adresse email valide.")
        return redirect(request.META.get("HTTP_REFERER", "core:home"))

    if not consent:
        messages.error(request, "Veuillez accepter les conditions de réception de la newsletter.")
        return redirect(request.META.get("HTTP_REFERER", "core:home"))

    # Extract client IP
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip_addr = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={
            "consent_given": True,
            "consent_timestamp": timezone.now(),
            "consent_ip": ip_addr,
            "source": request.POST.get("source", "website_form"),
            "status": "subscribed"
        }
    )

    if not created:
        # Existing subscriber re-subscribing with fresh consent
        subscriber.status = "subscribed"
        subscriber.consent_given = True
        subscriber.consent_timestamp = timezone.now()
        subscriber.consent_ip = ip_addr
        subscriber.save()

    # Sync with Brevo
    service = get_newsletter_service()
    service.sync_contact(subscriber)

    messages.success(request, "Merci ! Vous êtes bien inscrit à la newsletter technique de MickaelCode.")
    return redirect(request.META.get("HTTP_REFERER", "core:home"))


def unsubscribe_token_view(request, token):
    """
    1-click instant unsubscribe from newsletter using unique secret token.
    """
    subscriber = get_object_or_404(NewsletterSubscriber, unsubscribe_token=token)
    subscriber.unsubscribe()

    # Sync unsubscribe to provider
    service = get_newsletter_service()
    service.unsubscribe_contact(subscriber.email)

    return render(request, "marketing/unsubscribed.html", {"subscriber": subscriber})


def unsubscribe_view(request):
    """
    Manual unsubscribe form allowing user to input their email.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        subscriber = NewsletterSubscriber.objects.filter(email=email).first()
        if subscriber:
            subscriber.unsubscribe()
            service = get_newsletter_service()
            service.unsubscribe_contact(email)
        messages.success(request, f"L'adresse {email} a bien été désinscrite de nos listes de diffusion.")
        return render(request, "marketing/unsubscribed.html", {"email": email})

    return render(request, "marketing/unsubscribe_form.html")
