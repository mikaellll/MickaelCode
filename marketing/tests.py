from django.test import TestCase
from django.urls import reverse
from marketing.models import NewsletterSubscriber


class MarketingTests(TestCase):
    def test_subscribe_success_with_consent(self):
        url = reverse("marketing:subscribe")
        response = self.client.post(url, {
            "email": "subscriber@example.com",
            "consent": "on",
            "source": "unit_test"
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        subscriber = NewsletterSubscriber.objects.filter(email="subscriber@example.com").first()
        self.assertIsNotNone(subscriber)
        self.assertEqual(subscriber.status, "subscribed")
        self.assertTrue(subscriber.consent_given)

    def test_subscribe_without_consent_fails(self):
        url = reverse("marketing:subscribe")
        response = self.client.post(url, {
            "email": "noconsent@example.com",
            # consent omitted
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NewsletterSubscriber.objects.filter(email="noconsent@example.com").exists())

    def test_unsubscribe_via_token(self):
        subscriber = NewsletterSubscriber.objects.create(
            email="unsub@example.com",
            status="subscribed",
            consent_given=True
        )
        url = reverse("marketing:unsubscribe_token", kwargs={"token": subscriber.unsubscribe_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        subscriber.refresh_from_db()
        self.assertEqual(subscriber.status, "unsubscribed")

    def test_unsubscribe_via_form(self):
        subscriber = NewsletterSubscriber.objects.create(
            email="form_unsub@example.com",
            status="subscribed",
            consent_given=True
        )
        url = reverse("marketing:unsubscribe_view")
        response = self.client.post(url, {"email": "form_unsub@example.com"})
        self.assertEqual(response.status_code, 200)

        subscriber.refresh_from_db()
        self.assertEqual(subscriber.status, "unsubscribed")
