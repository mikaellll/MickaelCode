from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.post_list_view, name="post_list"),
    path("category/<slug:slug>/", views.category_detail_view, name="category_detail"),
    path("tag/<slug:slug>/", views.tag_detail_view, name="tag_detail"),
    path("<slug:slug>/", views.post_detail_view, name="post_detail"),
]
