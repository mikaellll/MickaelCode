from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.overview_view, name="overview"),
    path("courses/", views.my_courses_view, name="my_courses"),
    path("learning/", views.my_learning_view, name="my_learning"),
    path("purchases/", views.my_purchases_view, name="my_purchases"),
    path("notifications/", views.notifications_view, name="notifications"),
]
