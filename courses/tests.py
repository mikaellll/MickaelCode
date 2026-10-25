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

    def test_bunny_token_generation_algorithm(self):
        import hashlib
        from courses.services import VideoPlayerService
        token_key = "test-token-key-12345"
        video_id = "test-video-uuid-67890"
        library_id = "9999"

        signed_url = VideoPlayerService.generate_bunny_signed_url(
            library_id=library_id,
            video_id=video_id,
            token_key=token_key,
            expiration_seconds=3600
        )

        self.assertIn(f"https://iframe.mediadelivery.net/embed/{library_id}/{video_id}", signed_url)
        self.assertIn("token=", signed_url)
        self.assertIn("expires=", signed_url)

        # Extract expires and verify SHA-256 match
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(signed_url)
        params = parse_qs(parsed.query)
        token = params["token"][0]
        expires = params["expires"][0]

        expected_raw = f"{token_key}{video_id}{expires}"
        expected_token = hashlib.sha256(expected_raw.encode("utf-8")).hexdigest()
        self.assertEqual(token, expected_token)

    def test_bunny_player_renders_token_when_authorized(self):
        from courses.services import VideoPlayerService
        from django.test import override_settings

        self.paid_lesson.video_provider = "bunny"
        self.paid_lesson.video_id_or_url = "bunny-vid-123"
        self.paid_lesson.save()

        with override_settings(BUNNY_STREAM_LIBRARY_ID="12345", BUNNY_STREAM_TOKEN_KEY="secret-token-key"):
            html = VideoPlayerService.render_player(self.paid_lesson, user=self.user_enrolled)
            self.assertIn("bunny-stream-player", html)
            self.assertIn("https://iframe.mediadelivery.net/embed/12345/bunny-vid-123", html)
            self.assertIn("token=", html)
            self.assertIn("expires=", html)

    def test_bunny_player_blocks_unauthorized_user(self):
        from courses.services import VideoPlayerService
        self.paid_lesson.video_provider = "bunny"
        self.paid_lesson.video_id_or_url = "bunny-vid-456"
        self.paid_lesson.save()

        html = VideoPlayerService.render_player(self.paid_lesson, user=self.user_stranger)
        self.assertIn("Accès Réservé", html)
        self.assertNotIn("iframe", html)
        self.assertNotIn("bunny-vid-456", html)

    def test_save_video_position_endpoint(self):
        import json
        self.client.force_login(self.user_enrolled)
        url = reverse("courses:save_position", kwargs={"lesson_id": self.paid_lesson.id})

        response = self.client.post(
            url,
            data=json.dumps({"seconds": 125}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["saved_position"], 125)

        progress = LessonProgress.objects.get(user=self.user_enrolled, lesson=self.paid_lesson)
        self.assertEqual(progress.last_position_seconds, 125)

    def test_save_video_position_bounds_sanitization(self):
        import json
        self.client.force_login(self.user_enrolled)
        url = reverse("courses:save_position", kwargs={"lesson_id": self.paid_lesson.id})

        # Negative seconds should be sanitized to 0
        response_neg = self.client.post(
            url,
            data=json.dumps({"seconds": -50}),
            content_type="application/json"
        )
        self.assertEqual(response_neg.status_code, 200)
        self.assertEqual(response_neg.json()["saved_position"], 0)

        # Huge seconds should be capped
        response_huge = self.client.post(
            url,
            data=json.dumps({"seconds": 9999999}),
            content_type="application/json"
        )
        self.assertEqual(response_huge.status_code, 200)
        max_expected = (self.paid_lesson.duration_minutes * 60) + 3600
        self.assertEqual(response_huge.json()["saved_position"], max_expected)

    def test_save_video_position_unauthorized_rejected(self):
        import json
        self.client.force_login(self.user_stranger)
        url = reverse("courses:save_position", kwargs={"lesson_id": self.paid_lesson.id})

        response = self.client.post(
            url,
            data=json.dumps({"seconds": 60}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
