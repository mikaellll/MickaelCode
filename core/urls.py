from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("work/", views.work_view, name="work"),
    path("work/<slug:slug>/", views.project_detail_view, name="project_detail"),
    path("skills/", views.skills_view, name="skills"),
    path("contact/", views.contact_view, name="contact"),

    # Legal & Compliance
    path("mentions-legales/", views.legal_mentions_view, name="legal_mentions"),
    path("cgu-cgv/", views.cgu_cgv_view, name="cgu_cgv"),
    path("politique-de-confidentialite/", views.privacy_policy_view, name="privacy_policy"),

    # SEO & Crawlers
    path(
        "robots.txt",
        TemplateView.as_view(template_name="core/seo/robots.txt", content_type="text/plain"),
        name="robots_txt"
    ),
    path(
        "sitemap/",
        TemplateView.as_view(template_name="core/seo/sitemap_page.html"),
        name="sitemap"
    ),
]
