from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from courses.models import Course
from .models import PortfolioProject


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:about",
            "core:work",
            "core:skills",
            "core:contact",
            "blog:post_list",
            "courses:course_list",
            "core:legal_mentions",
            "core:cgu_cgv",
            "core:privacy_policy",
        ]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class CourseSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return Course.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return PortfolioProject.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.created_at
