from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from blog.models import Category, Post, Tag

User = get_user_model()


class BlogTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", email="author@example.com", password="pass")
        self.category = Category.objects.create(name="Django", slug="django")
        self.tag = Tag.objects.create(name="Web", slug="web")

        self.published_post = Post.objects.create(
            title="Article Public",
            slug="article-public",
            excerpt="Extrait article public",
            content_markdown="## Titre Markdown\n\nVoici du texte avec du `code inline` et <script>alert('bad');</script>",
            author=self.author,
            category=self.category,
            status="published"
        )
        self.published_post.tags.add(self.tag)

        self.draft_post = Post.objects.create(
            title="Article Brouillon",
            slug="article-brouillon",
            excerpt="Brouillon",
            content_markdown="Contenu secret",
            author=self.author,
            status="draft"
        )

    def test_post_list_displays_published_posts(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article Public")
        self.assertNotContains(response, "Article Brouillon")

    def test_published_post_detail(self):
        response = self.client.get(reverse("blog:post_detail", kwargs={"slug": "article-public"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article Public")
        self.assertContains(response, "Titre Markdown")

    def test_markdown_sanitizer_removes_scripts(self):
        rendered = self.published_post.render_markdown()
        self.assertNotIn("<script>", rendered)
        self.assertIn("<code>code inline</code>", rendered)

    def test_draft_post_forbidden_for_anonymous_users(self):
        response = self.client.get(reverse("blog:post_detail", kwargs={"slug": "article-brouillon"}))
        self.assertEqual(response.status_code, 404)

    def test_draft_post_accessible_by_staff(self):
        self.author.is_staff = True
        self.author.save()
        self.client.force_login(self.author)
        response = self.client.get(reverse("blog:post_detail", kwargs={"slug": "article-brouillon"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article Brouillon")
