from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Course, Module, Lesson, Enrollment, LessonProgress


class LessonInline(TabularInline):
    model = Lesson
    extra = 1
    fields = ["order", "title", "duration_minutes", "video_provider", "video_id_or_url", "is_free_preview", "status"]
    ordering = ["order"]


class ModuleInline(TabularInline):
    model = Module
    extra = 1
    fields = ["order", "title", "description"]
    ordering = ["order"]


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ["title", "level", "price", "currency", "status", "is_featured", "order", "created_at"]
    list_editable = ["status", "is_featured", "order"]
    list_filter = ["status", "level", "is_featured"]
    search_fields = ["title", "short_description", "description_markdown"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]
    fieldsets = (
        (
            "Informations Générales",
            {
                "fields": (
                    "title",
                    "slug",
                    "short_description",
                    "description_markdown",
                    "cover_image",
                    "level",
                    "order",
                )
            },
        ),
        (
            "Pédagogie & Prérequis",
            {
                "fields": (
                    "learning_objectives",
                    "prerequisites",
                )
            },
        ),
        (
            "Tarification & Monétisation",
            {
                "fields": (
                    "price",
                    "currency",
                    "stripe_price_id",
                    "status",
                    "is_featured",
                )
            },
        ),
        (
            "Référencement SEO",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                )
            },
        ),
    )


@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ["title", "course", "order"]
    list_filter = ["course"]
    search_fields = ["title", "description"]
    inlines = [LessonInline]
    ordering = ["course", "order"]


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = [
        "title",
        "module",
        "order",
        "duration_minutes",
        "video_provider",
        "is_free_preview",
        "status",
    ]
    list_editable = ["order", "is_free_preview", "status"]
    list_filter = ["status", "is_free_preview", "video_provider", "module__course"]
    search_fields = ["title", "description", "video_id_or_url"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ["user", "course", "status", "acquisition_source", "enrolled_at"]
    list_filter = ["status", "acquisition_source", "course"]
    search_fields = ["user__email", "user__username", "course__title"]
    readonly_fields = ["enrolled_at"]


@admin.register(LessonProgress)
class LessonProgressAdmin(ModelAdmin):
    list_display = ["user", "lesson", "is_completed", "last_position_seconds", "last_accessed_at"]
    list_filter = ["is_completed"]
    search_fields = ["user__email", "lesson__title"]
    readonly_fields = ["last_accessed_at", "completed_at"]
