from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    path("subscribe/", views.subscribe_view, name="subscribe"),
    path("unsubscribe/", views.unsubscribe_view, name="unsubscribe_view"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe_token_view, name="unsubscribe_token"),
]
