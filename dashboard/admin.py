from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import StudentNotification


@admin.register(StudentNotification)
class StudentNotificationAdmin(ModelAdmin):
    list_display = ["user", "title", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["user__email", "user__username", "title", "message"]
    readonly_fields = ["created_at"]
