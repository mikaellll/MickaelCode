from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order, PaymentWebhookEvent


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "order_reference",
        "user",
        "course",
        "amount",
        "currency",
        "status",
        "created_at",
    ]
    list_filter = ["status", "currency", "created_at"]
    search_fields = [
        "order_reference",
        "user__email",
        "user__username",
        "course__title",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
    ]
    readonly_fields = [
        "order_reference",
        "created_at",
        "updated_at",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
    ]


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(ModelAdmin):
    list_display = ["stripe_event_id", "event_type", "processed", "created_at"]
    list_filter = ["event_type", "processed", "created_at"]
    search_fields = ["stripe_event_id", "event_type"]
    readonly_fields = ["stripe_event_id", "event_type", "payload", "processed", "error_message", "created_at"]
