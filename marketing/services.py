"""
Newsletter & Commercial Campaign Service Abstraction.
Encapsulates API integration with Brevo (Sendinblue) and MailerLite,
while providing a local fallback for development and testing.
"""

import logging
import requests
from abc import ABC, abstractmethod
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class NewsletterProviderInterface(ABC):
    @abstractmethod
    def sync_contact(self, subscriber):
        pass

    @abstractmethod
    def unsubscribe_contact(self, email):
        pass


class BrevoNewsletterService(NewsletterProviderInterface):
    """
    Official Brevo API v3 integration using standard secure requests.
    Endpoint: https://api.brevo.com/v3/contacts
    """
    API_URL = "https://api.brevo.com/v3"

    def __init__(self, api_key=None, list_id=None):
        self.api_key = api_key or getattr(settings, "BREVO_API_KEY", "")
        self.list_id = list_id or getattr(settings, "BREVO_LIST_ID", 1)

    def _get_headers(self):
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key,
        }

    def sync_contact(self, subscriber):
        """
        Creates or updates a contact on Brevo with explicit GDPR opt-in.
        """
        if not self.api_key or self.api_key.startswith("xkeysib-placeholder"):
            logger.info(f"[Brevo Mock] Simulating contact sync for {subscriber.email}")
            subscriber.is_synced = True
            subscriber.last_synced_at = timezone.now()
            subscriber.brevo_contact_id = f"mock_brevo_{subscriber.id}"
            subscriber.save(update_fields=["is_synced", "last_synced_at", "brevo_contact_id"])
            return True

        url = f"{self.API_URL}/contacts"
        payload = {
            "email": subscriber.email,
            "attributes": {
                "PRENOM": subscriber.first_name,
                "CONSENT_DATE": subscriber.consent_timestamp.isoformat(),
                "SOURCE": subscriber.source,
            },
            "listIds": [int(self.list_id)],
            "updateEnabled": True,
        }

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=8)
            if response.status_code in [200, 201, 204]:
                data = response.json() if response.content else {}
                contact_id = str(data.get("id", ""))
                subscriber.brevo_contact_id = contact_id
                subscriber.is_synced = True
                subscriber.last_synced_at = timezone.now()
                subscriber.save(update_fields=["brevo_contact_id", "is_synced", "last_synced_at"])
                logger.info(f"Successfully synced contact {subscriber.email} to Brevo.")
                return True
            else:
                logger.error(f"Brevo API error syncing {subscriber.email}: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.exception(f"Exception connecting to Brevo: {e}")
            return False

    def unsubscribe_contact(self, email):
        """
        Unsubscribes a contact on Brevo.
        """
        if not self.api_key or self.api_key.startswith("xkeysib-placeholder"):
            logger.info(f"[Brevo Mock] Unsubscribed {email}")
            return True

        url = f"{self.API_URL}/contacts/{email}"
        payload = {"emailBlacklisted": True}
        try:
            response = requests.put(url, json=payload, headers=self._get_headers(), timeout=8)
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error unsubscribing contact on Brevo {email}: {e}")
            return False


class LocalMockNewsletterService(NewsletterProviderInterface):
    """
    Mock service for local development and unit tests.
    """
    def sync_contact(self, subscriber):
        subscriber.is_synced = True
        subscriber.last_synced_at = timezone.now()
        subscriber.brevo_contact_id = f"local_mock_{subscriber.id}"
        subscriber.save(update_fields=["is_synced", "last_synced_at", "brevo_contact_id"])
        return True

    def unsubscribe_contact(self, email):
        return True


def get_newsletter_service():
    """
    Factory function returning the configured newsletter service.
    """
    provider = getattr(settings, "NEWSLETTER_PROVIDER", "brevo").lower()
    if provider == "brevo":
        return BrevoNewsletterService()
    return LocalMockNewsletterService()
