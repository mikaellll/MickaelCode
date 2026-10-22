from django.conf import settings
from django.utils import timezone


def global_context(request):
    """
    Exposes global variables to all Django templates.
    """
    unread_notifications_count = 0
    enrolled_courses_count = 0

    if request.user.is_authenticated:
        from dashboard.models import StudentNotification
        from courses.models import Enrollment

        unread_notifications_count = StudentNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        enrolled_courses_count = Enrollment.objects.filter(
            user=request.user,
            status="active"
        ).count()

    return {
        "SITE_NAME": "MickaelCode",
        "SITE_TAGLINE": "Architecte Logiciel & Développeur Full-Stack Python / Django",
        "SITE_URL": getattr(settings, "SITE_URL", "https://mickaelcode.com"),
        "STRIPE_PUBLIC_KEY": getattr(settings, "STRIPE_PUBLIC_KEY", ""),
        "CURRENT_YEAR": timezone.now().year,
        "UNREAD_NOTIFICATIONS_COUNT": unread_notifications_count,
        "ENROLLED_COURSES_COUNT": enrolled_courses_count,
        "LINKEDIN_URL": "https://www.linkedin.com/in/mickael-developpeur/",
        "GITHUB_URL": "https://github.com/mickaelcode",
        "TWITTER_URL": "https://twitter.com/mickaelcode",
    }
