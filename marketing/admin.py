from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = [
        "email",
        "first_name",
        "status",
        "source",
        "consent_given",
        "consent_timestamp",
        "is_synced",
    ]
    list_filter = ["status", "consent_given", "is_synced", "source"]
    search_fields = ["email", "first_name", "brevo_contact_id"]
    readonly_fields = [
        "consent_timestamp",
        "consent_ip",
        "unsubscribe_token",
        "created_at",
        "updated_at",
        "last_synced_at",
    ]
    actions = ["sync_with_provider", "mark_unsubscribed"]

    def sync_with_provider(self, request, queryset):
        from .services import get_newsletter_service
        service = get_newsletter_service()
        count = 0
        for sub in queryset.filter(status="subscribed"):
            if service.sync_contact(sub):
                count += 1
        self.message_user(request, f"{count} contacts synchronisés avec succès.")
    sync_with_provider.short_description = "Synchroniser avec le fournisseur e-mail"

    def mark_unsubscribed(self, request, queryset):
        queryset.update(status="unsubscribed")
        self.message_user(request, "Les abonnés sélectionnés ont été désinscrits.")
    mark_unsubscribed.short_description = "Désinscrire les abonnés sélectionnés"
