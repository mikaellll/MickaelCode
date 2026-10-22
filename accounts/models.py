from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for MickaelCode platform.
    Uses email as a unique identifier and stores profile and consent fields.
    """
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )
    bio = models.TextField(blank=True, verbose_name="Biographie")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    newsletter_accepted = models.BooleanField(
        default=False,
        verbose_name="Consentement newsletter"
    )
    newsletter_consent_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date consentement newsletter"
    )
    terms_accepted = models.BooleanField(
        default=False,
        verbose_name="CGU / CGV acceptées"
    )
    stripe_customer_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="ID Client Stripe"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email or self.username

    def display_name(self):
        full = self.get_full_name()
        return full if full else (self.username or self.email.split("@")[0])

    def has_access_to_course(self, course):
        """
        Check if user has active enrollment for the given course.
        """
        if self.is_superuser or self.is_staff:
            return True
        return self.enrollments.filter(course=course, status="active").exists()
