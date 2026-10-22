from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course, Enrollment, Lesson, LessonProgress
from billing.models import Order
from .models import StudentNotification


@login_required
def overview_view(request):
    """
    Main student dashboard overview. Shows welcome message, enrolled courses,
    last accessed lesson with resume button, and suggested courses.
    """
    user = request.user
    enrollments = Enrollment.objects.filter(user=user, status="active").select_related("course")

    # Find last accessed lesson
    last_progress = LessonProgress.objects.filter(
        user=user
    ).select_related("lesson__module__course").order_by("-last_accessed_at").first()

    # Enrolled courses with calculated user progress
    enrolled_courses_data = []
    for enr in enrollments:
        progress_pct = enr.course.user_progress_percentage(user)
        enrolled_courses_data.append({
            "course": enr.course,
            "progress_pct": progress_pct,
            "enrolled_at": enr.enrolled_at,
        })

    # Available new courses not yet purchased
    enrolled_course_ids = [e.course_id for e in enrollments]
    available_courses = Course.objects.filter(status="published").exclude(id__in=enrolled_course_ids)[:3]

    # Recent orders
    recent_orders = Order.objects.filter(user=user).select_related("course")[:3]

    # Unread notifications
    notifications = StudentNotification.objects.filter(user=user)[:5]

    context = {
        "enrollments_count": enrollments.count(),
        "enrolled_courses_data": enrolled_courses_data,
        "last_progress": last_progress,
        "available_courses": available_courses,
        "recent_orders": recent_orders,
        "notifications": notifications,
    }
    return render(request, "dashboard/overview.html", context)


@login_required
def my_courses_view(request):
    """
    Catalog of all enrolled courses with filters for in-progress and completed.
    """
    user = request.user
    enrollments = Enrollment.objects.filter(user=user, status="active").select_related("course")

    courses_list = []
    for enr in enrollments:
        pct = enr.course.user_progress_percentage(user)
        courses_list.append({
            "course": enr.course,
            "progress_pct": pct,
            "is_completed": pct >= 100,
            "first_lesson": enr.course.first_lesson(),
        })

    return render(request, "dashboard/my_courses.html", {
        "courses_list": courses_list
    })


@login_required
def my_learning_view(request):
    """
    Detailed learning history showing completed lessons, time spent, and next steps.
    """
    user = request.user
    progresses = LessonProgress.objects.filter(user=user).select_related(
        "lesson__module__course"
    ).order_by("-last_accessed_at")

    completed_count = progresses.filter(is_completed=True).count()

    return render(request, "dashboard/my_learning.html", {
        "progresses": progresses,
        "completed_count": completed_count,
    })


@login_required
def my_purchases_view(request):
    """
    Orders history, receipts, order references, and payment statuses.
    """
    user = request.user
    orders = Order.objects.filter(user=user).select_related("course").order_by("-created_at")

    return render(request, "dashboard/my_purchases.html", {
        "orders": orders
    })


@login_required
def notifications_view(request):
    """
    Student notifications feed.
    """
    user = request.user
    notifications = StudentNotification.objects.filter(user=user).order_by("-created_at")

    # Mark all as read on visit
    StudentNotification.objects.filter(user=user, is_read=False).update(is_read=True)

    return render(request, "dashboard/notifications.html", {
        "notifications": notifications
    })
