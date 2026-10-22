from decimal import Decimal
import markdown
import bleach
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class CourseQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published")


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Débutant"),
        ("intermediate", "Intermédiaire"),
        ("advanced", "Avancé"),
        ("all_levels", "Tous niveaux"),
    ]

    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("published", "Publié"),
        ("archived", "Archivé"),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre de la formation")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    short_description = models.TextField(max_length=350, verbose_name="Description courte")
    description_markdown = models.TextField(verbose_name="Description détaillée (Markdown)")
    cover_image = models.ImageField(upload_to="courses/%Y/", verbose_name="Image de couverture")
    learning_objectives = models.TextField(
        verbose_name="Ce que vous allez apprendre",
        help_text="Un objectif par ligne pour une liste à puces claire."
    )
    prerequisites = models.TextField(blank=True, verbose_name="Prérequis")
    level = models.CharField(max_length=30, choices=LEVEL_CHOICES, default="intermediate", verbose_name="Niveau")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("49.00"), verbose_name="Prix")
    currency = models.CharField(max_length=10, default="EUR", verbose_name="Devise")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="Mise en avant sur l'accueil")
    stripe_price_id = models.CharField(max_length=120, blank=True, verbose_name="ID Prix Stripe")
    meta_title = models.CharField(max_length=150, blank=True, verbose_name="Titre SEO")
    meta_description = models.CharField(max_length=255, blank=True, verbose_name="Description SEO")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    objects = CourseQuerySet.as_manager()

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ["order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.price} {self.currency})"

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"slug": self.slug})

    def objectives_list(self):
        return [line.strip() for line in self.learning_objectives.splitlines() if line.strip()]

    def render_description(self):
        md = markdown.Markdown(extensions=["markdown.extensions.extra", "markdown.extensions.nl2br"])
        raw = md.convert(self.description_markdown)
        return bleach.clean(
            raw,
            tags=list(bleach.sanitizer.ALLOWED_TAGS) + ["p", "div", "span", "h3", "h4", "ul", "ol", "li", "strong", "em", "code"],
            strip=True
        )

    def total_lessons_count(self):
        return Lesson.objects.filter(module__course=self, status="published").count()

    def total_duration_minutes(self):
        total = self.modules.filter(lessons__status="published").aggregate(
            models.Sum("lessons__duration_minutes")
        )["lessons__duration_minutes__sum"]
        return total or 0

    def user_is_enrolled(self, user):
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        return self.enrollments.filter(user=user, status="active").exists()

    def user_progress_percentage(self, user):
        if not user or not user.is_authenticated:
            return 0
        total = self.total_lessons_count()
        if total == 0:
            return 0
        completed = LessonProgress.objects.filter(
            user=user,
            lesson__module__course=self,
            is_completed=True
        ).count()
        return min(100, int((completed / total) * 100))

    def first_lesson(self):
        return Lesson.objects.filter(
            module__course=self,
            status="published"
        ).order_by("module__order", "order").first()


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules", verbose_name="Formation")
    title = models.CharField(max_length=200, verbose_name="Titre du module")
    description = models.TextField(blank=True, verbose_name="Description du module")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre du module")

    class Meta:
        verbose_name = "Module de formation"
        verbose_name_plural = "Modules de formation"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"

    def published_lessons(self):
        return self.lessons.filter(status="published").order_by("order")


class Lesson(models.Model):
    VIDEO_PROVIDERS = [
        ("bunny", "Bunny Stream (Sécurisé)"),
        ("mux", "Mux Video (HLS Signé)"),
        ("embed", "Lecteur Intégré / HTML5"),
        ("youtube_unlisted", "Lien Vidéo Privé"),
    ]

    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("published", "Publié"),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons", verbose_name="Module")
    title = models.CharField(max_length=200, verbose_name="Titre de la leçon")
    slug = models.SlugField(max_length=220, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description / Notes de cours")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre dans le module")
    duration_minutes = models.PositiveIntegerField(default=10, verbose_name="Durée estimée (minutes)")
    video_provider = models.CharField(
        max_length=30,
        choices=VIDEO_PROVIDERS,
        default="embed",
        verbose_name="Fournisseur vidéo"
    )
    video_id_or_url = models.CharField(
        max_length=255,
        verbose_name="Identifiant vidéo ou URL protégée",
        help_text="ID Bunny Stream / Mux / URL intégrable sécurisée"
    )
    is_free_preview = models.BooleanField(
        default=False,
        verbose_name="Aperçu gratuit (accessible sans achat)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="published",
        verbose_name="Statut"
    )
    resources_text = models.TextField(
        blank=True,
        verbose_name="Ressources / Liens téléchargeables",
        help_text="Liens et fichiers utiles pour cette leçon."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.module.course.title} - {self.title}"

    def can_access(self, user):
        """
        Check if user has permission to watch this lesson.
        """
        if self.is_free_preview:
            return True
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return self.module.course.user_is_enrolled(user)

    def get_next_lesson(self):
        # Next in same module
        next_in_module = Lesson.objects.filter(
            module=self.module,
            order__gt=self.order,
            status="published"
        ).order_by("order").first()
        if next_in_module:
            return next_in_module
        # First lesson in next module
        next_module = Module.objects.filter(
            course=self.module.course,
            order__gt=self.module.order
        ).order_by("order").first()
        if next_module:
            return next_module.lessons.filter(status="published").order_by("order").first()
        return None

    def get_prev_lesson(self):
        # Prev in same module
        prev_in_module = Lesson.objects.filter(
            module=self.module,
            order__lt=self.order,
            status="published"
        ).order_by("-order").first()
        if prev_in_module:
            return prev_in_module
        # Last lesson in prev module
        prev_module = Module.objects.filter(
            course=self.module.course,
            order__lt=self.module.order
        ).order_by("-order").first()
        if prev_module:
            return prev_module.lessons.filter(status="published").order_by("-order").first()
        return None


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Actif"),
        ("revoked", "Révoqué"),
        ("refunded", "Remboursé"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Apprenant"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Formation"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    acquisition_source = models.CharField(
        max_length=60,
        default="stripe",
        verbose_name="Source d'acquisition"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name="Statut d'accès"
    )
    stripe_session_id = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="ID Session Stripe"
    )

    class Meta:
        verbose_name = "Inscription formation"
        verbose_name_plural = "Inscriptions formations"
        unique_together = ("user", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user} -> {self.course.title} ({self.status})"


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progresses",
        verbose_name="Utilisateur"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progresses",
        verbose_name="Leçon"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Terminé")
    last_position_seconds = models.PositiveIntegerField(default=0, verbose_name="Dernière position (sec)")
    last_accessed_at = models.DateTimeField(auto_now=True, verbose_name="Dernière consultation")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Complété le")

    class Meta:
        verbose_name = "Progression de leçon"
        verbose_name_plural = "Progressions de leçons"
        unique_together = ("user", "lesson")
        ordering = ["-last_accessed_at"]

    def __str__(self):
        status_str = "Terminé" if self.is_completed else f"{self.last_position_seconds}s"
        return f"{self.user} - {self.lesson.title}: {status_str}"

    def mark_as_completed(self):
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
