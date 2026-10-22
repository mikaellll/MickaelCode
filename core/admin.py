from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Skill, PortfolioProject, ContactMessage


def dashboard_callback(request, context):
    """
    Supplies real analytics and KPI metrics to Django Unfold Admin Dashboard.
    """
    from accounts.models import User
    from blog.models import Post
    from courses.models import Course, Enrollment
    from billing.models import Order
    from marketing.models import NewsletterSubscriber
    from django.db.models import Sum

    total_sales = Order.objects.filter(status="completed").aggregate(Sum("amount"))["amount__sum"] or 0
    recent_orders = Order.objects.select_related("user", "course").order_by("-created_at")[:5]
    recent_messages = ContactMessage.objects.order_by("-created_at")[:5]

    context.update({
        "kpis": [
            {
                "title": "Chiffre d'affaires",
                "metric": f"{total_sales:.2f} €",
                "footer": "Total ventes formations Stripe",
            },
            {
                "title": "Apprenants Inscrits",
                "metric": str(Enrollment.objects.filter(status="active").count()),
                "footer": "Accès actifs aux cours",
            },
            {
                "title": "Formations Publiées",
                "metric": str(Course.objects.filter(status="published").count()),
                "footer": "Catalogue actif",
            },
            {
                "title": "Abonnés Newsletter",
                "metric": str(NewsletterSubscriber.objects.filter(status="subscribed").count()),
                "footer": "Consentements valides",
            },
        ],
        "recent_orders": recent_orders,
        "recent_messages": recent_messages,
    })
    return context


@admin.register(Skill)
class SkillAdmin(ModelAdmin):
    list_display = ["name", "percentage", "category", "order", "is_featured"]
    list_editable = ["percentage", "order", "is_featured"]
    list_filter = ["category", "is_featured"]
    search_fields = ["name"]


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(ModelAdmin):
    list_display = ["title", "client", "order", "is_featured", "is_published", "created_at"]
    list_editable = ["order", "is_featured", "is_published"]
    list_filter = ["is_featured", "is_published"]
    search_fields = ["title", "description", "technologies"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ["name", "email", "subject", "is_processed", "created_at"]
    list_editable = ["is_processed"]
    list_filter = ["is_processed", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    readonly_fields = ["created_at", "ip_address"]
