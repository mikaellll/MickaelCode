from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPassword123!",
            terms_accepted=True,
        )

    def test_user_signup_success(self):
        url = reverse("accounts:signup")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "terms_accepted": True,
            "newsletter_accepted": False,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_terms_required(self):
        url = reverse("accounts:signup")
        data = {
            "username": "notermsuser",
            "email": "noterms@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "terms_accepted": False,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="notermsuser").exists())

    def test_user_login_with_email(self):
        url = reverse("accounts:login")
        response = self.client.post(url, {
            "login": "test@example.com",
            "password": "StrongPassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.id)

    def test_user_login_with_username(self):
        url = reverse("accounts:login")
        response = self.client.post(url, {
            "login": "testuser",
            "password": "StrongPassword123!",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.id)

    def test_user_logout(self):
        self.client.login(username="testuser", password="StrongPassword123!")
        url = reverse("accounts:logout")
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_reset_url_resolves(self):
        url = reverse("accounts:password_reset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
