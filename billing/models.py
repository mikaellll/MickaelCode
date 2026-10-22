import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models
from courses.models import Course


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente de paiement"),
        ("completed", "Payé avec succès"),
        ("failed", "Échoué"),
        ("refunded", "Remboursé"),
        ("canceled", "Annulé"),
    ]

    order_reference = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="Référence commande"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Client"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Formation commandée"
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Montant"
    )
    currency = models.CharField(
        max_length=10,
        default="EUR",
        verbose_name="Devise"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Statut"
    )
    stripe_checkout_session_id = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="ID Session Checkout Stripe"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="ID Intention Paiement Stripe"
    )
    receipt_url = models.URLField(
        blank=True,
        verbose_name="Reçu Stripe / Justificatif"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.order_reference:
            self.order_reference = f"MC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.order_reference} - {self.course.title} ({self.amount} {self.currency}) [{self.get_status_display()}]"


class PaymentWebhookEvent(models.Model):
    """
    Guarantees idempotency and traceability for incoming Stripe webhooks.
    """
    stripe_event_id = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        verbose_name="ID Événement Stripe"
    )
    event_type = models.CharField(
        max_length=100,
        verbose_name="Type d'événement"
    )
    payload = models.JSONField(
        verbose_name="Payload JSON"
    )
    processed = models.BooleanField(
        default=False,
        verbose_name="Traité avec succès"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Erreur éventuelle"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Reçu le")

    class Meta:
        verbose_name = "Événement Webhook Stripe"
        verbose_name_plural = "Événements Webhook Stripe"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} ({self.stripe_event_id})"
