from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "newsletter_accepted",
        "date_joined",
    ]
    list_filter = ["is_staff", "is_superuser", "newsletter_accepted", "date_joined"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Informations personnelles",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "avatar",
                    "bio",
                    "phone",
                )
            },
        ),
        (
            "Consentements & RGPD",
            {
                "fields": (
                    "newsletter_accepted",
                    "newsletter_consent_date",
                    "terms_accepted",
                    "stripe_customer_id",
                )
            },
        ),
        (
            "Permissions & Rôles",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )
