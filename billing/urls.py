from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("checkout/<slug:course_slug>/", views.create_checkout_session_view, name="create_checkout_session"),
    path("webhook/", views.stripe_webhook_view, name="stripe_webhook"),
    path("success/", views.payment_success_view, name="payment_success"),
    path("cancel/", views.payment_cancel_view, name="payment_cancel"),
]
