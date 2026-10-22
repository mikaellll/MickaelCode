from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list_view, name="course_list"),
    path("<slug:slug>/", views.course_detail_view, name="course_detail"),
    path("<slug:course_slug>/lessons/<int:lesson_id>/", views.lesson_player_view, name="lesson_player"),
    path("progress/<int:lesson_id>/toggle/", views.toggle_lesson_progress_view, name="toggle_progress"),
    path("progress/<int:lesson_id>/position/", views.save_video_position_view, name="save_position"),
]
