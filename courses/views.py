import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Course, Module, Lesson, Enrollment, LessonProgress
from .services import VideoPlayerService


def course_list_view(request):
    """
    Public catalog of video courses with filters for skill levels and search.
    """
    level_filter = request.GET.get("level", "").strip()
    search_query = request.GET.get("q", "").strip()

    courses = Course.objects.published().prefetch_related("modules__lessons")

    if level_filter:
        courses = courses.filter(level=level_filter)
    if search_query:
        courses = courses.filter(title__icontains=search_query)

    context = {
        "courses": courses,
        "selected_level": level_filter,
        "search_query": search_query,
        "level_choices": Course.LEVEL_CHOICES,
    }
    return render(request, "courses/course_list.html", context)


def course_detail_view(request, slug):
    """
    Public course landing page with syllabus, curriculum preview, learning goals and checkout CTA.
    """
    course = get_object_or_404(Course, slug=slug, status="published")
    is_enrolled = course.user_is_enrolled(request.user)
    modules = course.modules.prefetch_related("lessons").order_by("order")

    first_lesson = course.first_lesson()
    user_progress = course.user_progress_percentage(request.user) if is_enrolled else 0

    context = {
        "course": course,
        "is_enrolled": is_enrolled,
        "modules": modules,
        "first_lesson": first_lesson,
        "user_progress": user_progress,
    }
    return render(request, "courses/course_detail.html", context)


def lesson_player_view(request, course_slug, lesson_id):
    """
    Interactive lesson workspace. Strictly protects private videos server-side.
    """
    course = get_object_or_404(Course, slug=course_slug, status="published")
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course, status="published")

    can_access = lesson.can_access(request.user)

    if not can_access:
        # Access denied: display paywall with direct Stripe Checkout option
        return render(request, "courses/paywall.html", {
            "course": course,
            "lesson": lesson,
        }, status=403)

    # User is authorized: fetch or create progress tracking
    progress = None
    if request.user.is_authenticated:
        progress, _ = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        progress.last_accessed_at = timezone.now()
        progress.save(update_fields=["last_accessed_at"])

    # Render video player safely via abstraction with server-side access check
    player_html = VideoPlayerService.render_player(lesson, user=request.user)

    # Syllabus for sidebar navigation
    modules = course.modules.prefetch_related("lessons").order_by("order")

    # Completed lesson IDs for checkmarks in sidebar
    completed_lesson_ids = set()
    if request.user.is_authenticated:
        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__module__course=course,
                is_completed=True
            ).values_list("lesson_id", flat=True)
        )

    context = {
        "course": course,
        "lesson": lesson,
        "player_html": player_html,
        "modules": modules,
        "progress": progress,
        "completed_lesson_ids": completed_lesson_ids,
        "next_lesson": lesson.get_next_lesson(),
        "prev_lesson": lesson.get_prev_lesson(),
    }
    return render(request, "courses/lesson_player.html", context)


@login_required
@require_POST
def toggle_lesson_progress_view(request, lesson_id):
    """
    Mark a lesson as completed or in progress.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson.can_access(request.user):
        return HttpResponseForbidden("Accès refusé à cette leçon.")

    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.is_completed = not progress.is_completed
    if progress.is_completed:
        progress.completed_at = timezone.now()
    else:
        progress.completed_at = None
    progress.save()

    # If it's an AJAX request, return JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
        course = lesson.module.course
        return JsonResponse({
            "success": True,
            "is_completed": progress.is_completed,
            "course_progress": course.user_progress_percentage(request.user)
        })

    messages.success(request, "Progression mise à jour.")
    return redirect("courses:lesson_player", course_slug=lesson.module.course.slug, lesson_id=lesson.id)


@login_required
@require_POST
def save_video_position_view(request, lesson_id):
    """
    AJAX endpoint called periodically during video playback to save the exact timestamp.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not lesson.can_access(request.user):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body.decode("utf-8"))
        seconds = int(data.get("seconds", 0))
    except Exception:
        seconds = 0

    # Bounds validation: non-negative and capped at lesson duration + buffer
    max_seconds = (lesson.duration_minutes * 60) + 3600
    if seconds < 0:
        seconds = 0
    elif seconds > max_seconds:
        seconds = max_seconds

    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    progress.last_position_seconds = seconds
    progress.save(update_fields=["last_position_seconds", "last_accessed_at"])

    return JsonResponse({"success": True, "saved_position": seconds})
