from django.conf import settings
from django.db import models


class StudentNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Apprenant"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    link = models.CharField(max_length=255, blank=True, verbose_name="Lien d'action")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")

    class Meta:
        verbose_name = "Notification apprenant"
        verbose_name_plural = "Notifications apprenants"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title} ({'Lu' if self.is_read else 'Non lu'})"
