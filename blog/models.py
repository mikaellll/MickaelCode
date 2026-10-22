import math
import bleach
import markdown
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Catégorie d'articles"
        verbose_name_plural = "Catégories d'articles"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category_detail", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tag")
    slug = models.SlugField(max_length=60, unique=True, blank=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status="published",
            published_at__lte=timezone.now()
        )


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("published", "Publié"),
        ("archived", "Archivé"),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    excerpt = models.TextField(max_length=400, verbose_name="Extrait / Résumé")
    content_markdown = models.TextField(
        verbose_name="Contenu en Markdown",
        help_text="Rédigez votre article en Markdown avec blocs de code ```python ... ```."
    )
    cover_image = models.ImageField(
        upload_to="blog/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Image de couverture"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blog_posts",
        verbose_name="Auteur"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Catégorie"
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name="Tags"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Statut"
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de publication"
    )
    reading_time_minutes = models.PositiveIntegerField(
        default=3,
        verbose_name="Temps de lecture estimé (min)"
    )
    meta_title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Titre SEO"
    )
    meta_description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Description SEO"
    )
    social_image = models.ImageField(
        upload_to="blog/social/%Y/",
        blank=True,
        null=True,
        verbose_name="Image de partage social (Open Graph)"
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de vues"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Compute estimated reading time (approx 200 words/min)
        if self.content_markdown:
            words = len(self.content_markdown.split())
            self.reading_time_minutes = max(1, math.ceil(words / 200))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def is_public(self):
        return self.status == "published" and self.published_at <= timezone.now()

    def render_markdown(self):
        """
        Converts Markdown to sanitized, safe HTML.
        Blocks raw script execution or unsafe tags while preserving code blocks and standard styling.
        """
        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.extra",
                "markdown.extensions.codehilite",
                "markdown.extensions.toc",
                "markdown.extensions.nl2br",
                "markdown.extensions.sane_lists",
            ]
        )
        raw_html = md.convert(self.content_markdown)

        # Whitelist safe tags and attributes
        allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
            "p", "div", "span", "pre", "code", "h1", "h2", "h3", "h4", "h5", "h6",
            "img", "table", "thead", "tbody", "tr", "th", "td", "blockquote",
            "hr", "br", "ul", "ol", "li", "strong", "em", "a", "del"
        ]
        allowed_attrs = {
            "*": ["class", "id"],
            "a": ["href", "title", "target", "rel"],
            "img": ["src", "alt", "title", "width", "height", "loading"],
            "code": ["class"],
            "pre": ["class"],
        }
        allowed_protocols = ["http", "https", "mailto"]

        sanitized_html = bleach.clean(
            raw_html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            protocols=allowed_protocols,
            strip=True
        )
        return sanitized_html
