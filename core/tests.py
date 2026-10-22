from django.test import TestCase
from django.urls import reverse
from core.models import ContactMessage, PortfolioProject, Skill


class CoreTests(TestCase):
    def setUp(self):
        self.project = PortfolioProject.objects.create(
            title="Projet Test",
            slug="projet-test",
            description="Description du projet test",
            technologies="Django, PostgreSQL",
            is_published=True,
        )
        self.skill = Skill.objects.create(
            name="Django",
            percentage=90,
            category="backend"
        )

    def test_home_page_status(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello,")
        self.assertContains(response, "Mickael")

    def test_about_page_status(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Marseille")

    def test_work_page_status(self):
        response = self.client.get(reverse("core:work"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Projet Test")

    def test_project_detail_page(self):
        response = self.client.get(reverse("core:project_detail", kwargs={"slug": "projet-test"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Projet Test")

    def test_skills_page_status(self):
        response = self.client.get(reverse("core:skills"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

    def test_contact_form_submission(self):
        url = reverse("core:contact")
        response = self.client.post(url, {
            "name": "Jean Dupont",
            "email": "jean@example.com",
            "subject": "Mission Freelance",
            "message": "Bonjour, je souhaite vous confier la refonte de mon SaaS.",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email="jean@example.com").exists())

    def test_robots_txt(self):
        response = self.client.get(reverse("core:robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response["Content-Type"])

    def test_custom_404_page(self):
        response = self.client.get("/cette-page-nexiste-pas-du-tout-404/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
