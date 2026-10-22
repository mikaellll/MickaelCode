import uuid
from django.db import models
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    STATUS_CHOICES = [
        ("subscribed", "Abonné"),
        ("unsubscribed", "Désabonné"),
    ]

    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    first_name = models.CharField(max_length=80, blank=True, verbose_name="Prénom")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="subscribed",
        verbose_name="Statut"
    )
    consent_given = models.BooleanField(
        default=True,
        verbose_name="Consentement explicite accordé"
    )
    consent_timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date et heure du consentement"
    )
    consent_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP du consentement"
    )
    source = models.CharField(
        max_length=80,
        default="website_form",
        verbose_name="Source du consentement"
    )
    unsubscribe_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Jeton de désinscription unique"
    )
    brevo_contact_id = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="ID Contact Fournisseur (Brevo/MailerLite)"
    )
    is_synced = models.BooleanField(
        default=False,
        verbose_name="Synchronisé avec le fournisseur"
    )
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière synchronisation"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Inscrit le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ["-consent_timestamp"]

    def __str__(self):
        return f"{self.email} [{self.get_status_display()}]"

    def unsubscribe(self):
        self.status = "unsubscribed"
        self.save(update_fields=["status", "updated_at"])
