from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Tag, Post


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = [
        "title",
        "author",
        "category",
        "status",
        "published_at",
        "reading_time_minutes",
        "views_count",
    ]
    list_filter = ["status", "category", "tags", "published_at"]
    search_fields = ["title", "excerpt", "content_markdown"]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["category", "tags", "author"]
    readonly_fields = ["reading_time_minutes", "views_count", "created_at", "updated_at"]
    fieldsets = (
        (
            "Contenu de l'article",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "category",
                    "tags",
                    "cover_image",
                    "excerpt",
                    "content_markdown",
                )
            },
        ),
        (
            "Publication & Visibilité",
            {
                "fields": (
                    "status",
                    "published_at",
                    "reading_time_minutes",
                    "views_count",
                )
            },
        ),
        (
            "Optimisation SEO & Réseaux Sociaux",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "social_image",
                )
            },
        ),
        (
            "Traçabilité",
            {"fields": ("created_at", "updated_at")},
        ),
    )
