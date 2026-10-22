from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, TemplateView, View
from blog.models import Post
from courses.models import Course
from .forms import ContactForm
from .models import PortfolioProject, Skill, ContactMessage


def home_view(request):
    """
    Home page preserving the original visual elements (hero, typography, geometric accents)
    while introducing the new courses and blog modules.
    """
    featured_projects = PortfolioProject.objects.filter(is_published=True, is_featured=True)[:4]
    featured_courses = Course.objects.filter(status="published", is_featured=True)[:3]
    latest_posts = Post.objects.published()[:3]
    featured_skills = Skill.objects.filter(is_featured=True)[:6]

    context = {
        "featured_projects": featured_projects,
        "featured_courses": featured_courses,
        "latest_posts": latest_posts,
        "featured_skills": featured_skills,
    }
    return render(request, "core/home.html", context)


def about_view(request):
    """
    About page preserving the original bio, Marseille location, MMA and family passions,
    and visual animated background canvas.
    """
    skills = Skill.objects.all()
    return render(request, "core/about.html", {"skills": skills})


def work_view(request):
    """
    Portfolio showcase of client projects and open-source applications.
    """
    projects = PortfolioProject.objects.filter(is_published=True)
    return render(request, "core/work.html", {"projects": projects})


def project_detail_view(request, slug):
    """
    Detailed case study for a portfolio project.
    """
    project = get_object_or_404(PortfolioProject, slug=slug, is_published=True)
    related_projects = PortfolioProject.objects.filter(is_published=True).exclude(id=project.id)[:3]
    return render(request, "core/project_detail.html", {
        "project": project,
        "related_projects": related_projects
    })


def skills_view(request):
    """
    Technical skills and experience page with interactive progress bars.
    """
    skills = Skill.objects.all()
    return render(request, "core/skills.html", {"skills": skills})


def contact_view(request):
    """
    Contact form with server-side validation and database persistence.
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            # Retrieve client IP
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                contact.ip_address = x_forwarded_for.split(",")[0]
            else:
                contact.ip_address = request.META.get("REMOTE_ADDR")
            contact.save()
            messages.success(request, "Merci Mickael a bien reçu votre message. Une réponse vous sera apportée sous 24h.")
            return redirect("core:contact")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire ci-dessous.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data["name"] = request.user.display_name()
            initial_data["email"] = request.user.email
        form = ContactForm(initial=initial_data)

    return render(request, "core/contact.html", {"form": form})


def legal_mentions_view(request):
    return render(request, "core/legal/mentions.html")


def cgu_cgv_view(request):
    return render(request, "core/legal/cgu_cgv.html")


def privacy_policy_view(request):
    return render(request, "core/legal/privacy.html")


def custom_404_view(request, exception=None):
    return render(request, "core/errors/404.html", status=404)


def custom_500_view(request):
    return render(request, "core/errors/500.html", status=500)
