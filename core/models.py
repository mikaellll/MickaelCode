from django.db import models
from django.utils.text import slugify


class Skill(models.Model):
    """Technical skill displayed on the skills page and portfolio."""
    CATEGORY_CHOICES = [
        ("backend", "Backend & Architecture"),
        ("frontend", "Frontend & UI"),
        ("devops", "DevOps & Cloud"),
        ("tools", "CMS & Outils"),
    ]
    name = models.CharField(max_length=80, verbose_name="Nom de la compétence")
    percentage = models.PositiveIntegerField(default=80, verbose_name="Niveau (%)")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="backend", verbose_name="Catégorie")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_featured = models.BooleanField(default=True, verbose_name="Mis en avant")

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class PortfolioProject(models.Model):
    """Showcase project for the portfolio / work page."""
    title = models.CharField(max_length=150, verbose_name="Titre du projet")
    slug = models.SlugField(max_length=160, unique=True, blank=True, verbose_name="Slug")
    tagline = models.CharField(max_length=255, blank=True, verbose_name="Accroche courte")
    description = models.TextField(verbose_name="Description détaillée")
    client = models.CharField(max_length=120, blank=True, verbose_name="Client / Contexte")
    image = models.ImageField(upload_to="projects/%Y/", verbose_name="Image principale")
    live_url = models.URLField(blank=True, verbose_name="Lien vers le site en ligne")
    github_url = models.URLField(blank=True, verbose_name="Dépôt GitHub")
    technologies = models.CharField(max_length=255, verbose_name="Technologies (ex: Django, Tailwind, PostgreSQL)")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    is_featured = models.BooleanField(default=True, verbose_name="Projet vedette")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    meta_title = models.CharField(max_length=150, blank=True, verbose_name="Titre SEO")
    meta_description = models.CharField(max_length=255, blank=True, verbose_name="Description SEO")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Réalisation"
        verbose_name_plural = "Réalisations"
        ordering = ["order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def tech_list(self):
        return [t.strip() for t in self.technologies.split(",") if t.strip()]


class ContactMessage(models.Model):
    """Direct message sent from the contact form."""
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse email")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    is_processed = models.BooleanField(default=False, verbose_name="Traité")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.email} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
