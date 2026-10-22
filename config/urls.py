"""
URL configuration for MickaelCode platform.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from core.sitemaps import StaticViewSitemap, BlogPostSitemap, CourseSitemap, ProjectSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "courses": CourseSitemap,
    "blog": BlogPostSitemap,
    "projects": ProjectSitemap,
}

urlpatterns = [
    # Administration
    path("admin/", admin.site.urls),

    # XML Sitemap
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),

    # Applications
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("blog/", include("blog.urls")),
    path("courses/", include("courses.urls")),
    path("billing/", include("billing.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("marketing/", include("marketing.urls")),
]

# Media uploads serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Error Views
handler404 = "core.views.custom_404_view"
handler500 = "core.views.custom_500_view"
