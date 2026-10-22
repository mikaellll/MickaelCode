from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from courses.models import Course, Module, Lesson, Enrollment, LessonProgress

User = get_user_model()


class CoursesTests(TestCase):
    def setUp(self):
        self.user_enrolled = User.objects.create_user(
            username="buyer", email="buyer@example.com", password="password"
        )
        self.user_stranger = User.objects.create_user(
            username="stranger", email="stranger@example.com", password="password"
        )

        self.course = Course.objects.create(
            title="Formation Django Test",
            slug="formation-django-test",
            short_description="Description courte",
            description_markdown="Description détaillée",
            price=Decimal("49.00"),
            currency="EUR",
            status="published",
        )

        self.module = Module.objects.create(
            course=self.course,
            title="Module 1",
            order=1
        )

        self.free_lesson = Lesson.objects.create(
            module=self.module,
            title="Leçon Gratuite",
            order=1,
            duration_minutes=10,
            video_provider="embed",
            video_id_or_url="video_1",
            is_free_preview=True,
            status="published"
        )

        self.paid_lesson = Lesson.objects.create(
            module=self.module,
            title="Leçon Payante",
            order=2,
            duration_minutes=20,
            video_provider="embed",
            video_id_or_url="video_2",
            is_free_preview=False,
            status="published"
        )

        # Enroll user_enrolled
        Enrollment.objects.create(
            user=self.user_enrolled,
            course=self.course,
            status="active"
        )

    def test_course_list_page(self):
        response = self.client.get(reverse("courses:course_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formation Django Test")

    def test_course_detail_page(self):
        response = self.client.get(reverse("courses:course_detail", kwargs={"slug": "formation-django-test"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formation Django Test")
        self.assertContains(response, "Leçon Gratuite")

    def test_free_preview_accessible_by_anonymous(self):
        url = reverse("courses:lesson_player", kwargs={"course_slug": self.course.slug, "lesson_id": self.free_lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leçon Gratuite")

    def test_paid_lesson_blocked_for_non_enrolled_user(self):
        self.client.force_login(self.user_stranger)
        url = reverse("courses:lesson_player", kwargs={"course_slug": self.course.slug, "lesson_id": self.paid_lesson.id})
        response = self.client.get(url)
        # Server must respond with 403 Forbidden and show paywall
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Cette leçon est réservée aux inscrits", status_code=403)

    def test_paid_lesson_accessible_by_enrolled_user(self):
        self.client.force_login(self.user_enrolled)
        url = reverse("courses:lesson_player", kwargs={"course_slug": self.course.slug, "lesson_id": self.paid_lesson.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leçon Payante")

    def test_toggle_lesson_progress(self):
        self.client.force_login(self.user_enrolled)
        url = reverse("courses:toggle_progress", kwargs={"lesson_id": self.paid_lesson.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        progress = LessonProgress.objects.get(user=self.user_enrolled, lesson=self.paid_lesson)
        self.assertTrue(progress.is_completed)
