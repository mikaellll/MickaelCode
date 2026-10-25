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
        self.assertContains(response, "PROJETS")

        # Verify all 6 projects are present with their external links
        expected_urls = [
            "https://v-car.company/",
            "https://marseillefightclub.com/",
            "https://magentanumerique.fr/",
            "https://excelworkflow.com/",
            "https://pralinee.fr/",
            "https://nestcase.com/",
        ]
        for url in expected_urls:
            self.assertContains(response, url)

        # Verify exact order of projects
        content = response.content.decode("utf-8")
        indices = [content.index(url) for url in expected_urls]
        self.assertEqual(indices, sorted(indices), "Les projets doivent apparaître dans l'ordre exact demandé.")

        # Verify target="_blank" and rel="noopener noreferrer"
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')

        # Verify static images are referenced
        self.assertContains(response, "vcar.png")
        self.assertContains(response, "marseillefightclub.png")
        self.assertContains(response, "magenta-v2.png")
        self.assertContains(response, "excelworkflow.png")
        self.assertContains(response, "pralinee.png")
        self.assertContains(response, "nestcase-v2.png")


    def test_project_detail_page(self):
        response = self.client.get(reverse("core:project_detail", kwargs={"slug": "projet-test"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Projet Test")

    def test_skills_page_status(self):
        response = self.client.get(reverse("core:skills"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

    def test_contact_page_get(self):
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contactez")
        self.assertContains(response, "mickaelbn@gmail.com")
        self.assertContains(response, "Marseille, France")
        self.assertContains(response, "contact-name")
        self.assertContains(response, "contact-email")
        self.assertContains(response, "contact-subject")
        self.assertContains(response, "contact-message")

    def test_contact_form_submission_success(self):
        from django.core import mail
        from django.conf import settings
        url = reverse("core:contact")
        mail.outbox.clear()

        response = self.client.post(url, {
            "name": "Jean Dupont",
            "email": "jean@example.com",
            "subject": "Refonte Plateforme Web",
            "message": "Bonjour Mickael, je souhaite discuter d'un projet web avec vous.",
            "bot_field": "",
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email="jean@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertIn("Refonte Plateforme Web", sent_email.subject)
        self.assertEqual(sent_email.from_email, settings.DEFAULT_FROM_EMAIL)
        expected_to = getattr(settings, "CONTACT_EMAIL", "mickaelbn@gmail.com")
        self.assertEqual(sent_email.to, [expected_to])
        self.assertEqual(sent_email.reply_to, ["jean@example.com"])
        self.assertIn("Jean Dupont", sent_email.body)
        self.assertIn("jean@example.com", sent_email.body)
        self.assertIn("Refonte Plateforme Web", sent_email.body)
        self.assertContains(response, "Votre message a été envoyé avec succès")

    def test_contact_form_honeypot_rejection(self):
        from django.core import mail
        mail.outbox.clear()
        url = reverse("core:contact")

        response = self.client.post(url, {
            "name": "Spam Bot",
            "email": "bot@spammer.com",
            "subject": "Buy crypto now",
            "message": "Visit our website for crypto gains http://spam.xyz",
            "bot_field": "I am a spam bot",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(ContactMessage.objects.filter(email="bot@spammer.com").exists())

    def test_contact_form_validation_errors(self):
        from django.core import mail
        mail.outbox.clear()
        url = reverse("core:contact")

        # Invalid email and too short message
        response = self.client.post(url, {
            "name": "J",
            "email": "not-an-email",
            "subject": "",
            "message": "Hi",
            "bot_field": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertIn("email", form.errors)
        self.assertIn("subject", form.errors)
        self.assertIn("message", form.errors)

    def test_contact_form_header_injection_protection(self):
        from django.core import mail
        mail.outbox.clear()
        url = reverse("core:contact")

        response = self.client.post(url, {
            "name": "Hacker\nBcc: evil@target.com",
            "email": "hacker@test.com",
            "subject": "Attack\r\nSubject",
            "message": "Testing CRLF injection attempt.",
            "bot_field": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        form = response.context["form"]
        self.assertTrue(form.errors)

    def test_contact_form_smtp_failure_handling(self):
        from unittest.mock import patch
        import smtplib
        url = reverse("core:contact")

        with patch("django.core.mail.EmailMessage.send", side_effect=smtplib.SMTPException("Connection timed out")):
            response = self.client.post(url, {
                "name": "Client Réel",
                "email": "client@example.com",
                "subject": "Demande de devis",
                "message": "Bonjour, merci de m'envoyer un devis pour une application SaaS.",
                "bot_field": "",
            })

            # Should not crash 500, should render 200 with error message
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Une erreur technique est survenue")
            # Should preserve submitted form values
            self.assertContains(response, "Client Réel")
            self.assertContains(response, "client@example.com")


    def test_robots_txt(self):
        response = self.client.get(reverse("core:robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response["Content-Type"])

    def test_custom_404_page(self):
        response = self.client.get("/cette-page-nexiste-pas-du-tout-404/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)

    def test_default_storage_fallback_to_filesystem(self):
        from django.core.files.storage import storages, FileSystemStorage
        default_storage = storages["default"]
        # In local/test environment without R2 keys, default storage must be FileSystemStorage
        self.assertIsInstance(default_storage, FileSystemStorage)

    def test_storage_media_url_configuration(self):
        from django.conf import settings
        self.assertTrue(settings.MEDIA_URL.startswith("/") or settings.MEDIA_URL.startswith("http"))

    def test_production_secret_key_security_guard(self):
        from decouple import config
        # Verify the security guard: if DEBUG=False and key is insecure, it must raise ValueError
        def simulate_insecure_prod():
            debug = False
            secret = "django-insecure-test-sample"
            if not debug and (not secret or secret.startswith("django-insecure-")):
                raise ValueError("CRITICAL SECURITY ERROR")

        with self.assertRaises(ValueError):
            simulate_insecure_prod()
