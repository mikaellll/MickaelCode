import logging
import time
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, TemplateView, View
from blog.models import Post
from courses.models import Course
from .forms import ContactForm
from .models import PortfolioProject, Skill, ContactMessage

logger = logging.getLogger(__name__)



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
    About page preserving the original bio, Marseille location, and passions.
    """
    skills = Skill.objects.all()
    return render(request, "core/about.html", {"skills": skills})


# Showcase projects in exact required order
PROJECTS_SHOWCASE = [
    {
        "name": "V-Car",
        "url": "https://v-car.company/",
        "image": "img/projects/vcar.png",
        "tagline": "Plateforme de convoyage automobile et gestion logistique",
    },
    {
        "name": "Marseille Fight Club",
        "url": "https://marseillefightclub.com/",
        "image": "img/projects/marseillefightclub.png",
        "tagline": "Club de Boxe & MMA à Marseille, réservation et gestion des adhérents",
    },
    {
        "name": "Magenta Numérique",
        "url": "https://magentanumerique.fr/",
        "image": "img/projects/magenta-v2.png",
        "tagline": "Imprimerie Grand Format à Marseille et atelier de production",
    },
    {
        "name": "Excel Workflow",
        "url": "https://excelworkflow.com/",
        "image": "img/projects/excelworkflow.png",
        "tagline": "Formations et automatisation des flux Excel, Python & Power BI",
    },
    {
        "name": "Pralinée",
        "url": "https://pralinee.fr/",
        "image": "img/projects/pralinee.png",
        "tagline": "Boulangerie & Pâtisserie artisanale, vitrine et commandes en ligne",
    },
    {
        "name": "Nestcase",
        "url": "https://nestcase.com/",
        "image": "img/projects/nestcase-v2.png",
        "tagline": "Boutique d'accessoires High-Tech et protection connectée",
    },
]


def work_view(request):
    """
    Portfolio showcase of client projects in the exact requested order.
    """
    return render(request, "core/work.html", {"projects": PROJECTS_SHOWCASE})



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
    Contact form with server-side validation, anti-spam protections,
    database persistence, and transactional email dispatch.
    """
    if request.method == "POST":
        form = ContactForm(request.POST)

        # Rate-limiting / anti-flood check: max 1 submission every 10 seconds per session
        last_submission = request.session.get("last_contact_submission_time")
        now = time.time()
        if last_submission and (now - last_submission) < 10:
            messages.error(request, "Veuillez patienter quelques instants avant d'envoyer un nouveau message.")
            return render(request, "core/contact.html", {"form": form})

        if form.is_valid():
            contact = form.save(commit=False)
            # Retrieve client IP
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(",")[0].strip()
            else:
                client_ip = request.META.get("REMOTE_ADDR", "")
            contact.ip_address = client_ip
            contact.save()

            # Email dispatching
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            recipient_email = getattr(settings, "CONTACT_EMAIL", "mickaelbn@gmail.com")
            from_email = settings.DEFAULT_FROM_EMAIL

            email_subject = f"[Contact MickaelCode] {subject}"
            email_body = (
                f"Nouveau message reçu depuis le formulaire de contact MickaelCode :\n"
                f"--------------------------------------------------\n"
                f"Nom       : {name}\n"
                f"Email     : {email}\n"
                f"Sujet     : {subject}\n"
                f"IP        : {client_ip or 'Inconnue'}\n"
                f"--------------------------------------------------\n\n"
                f"Message :\n{message}\n"
            )

            try:
                email_message = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=from_email,
                    to=[recipient_email],
                    reply_to=[email],
                )
                email_message.send(fail_silently=False)

                # Record successful submission timestamp to prevent double-click abuse
                request.session["last_contact_submission_time"] = now
                messages.success(request, "Votre message a été envoyé avec succès ! Je vous répondrai dans les plus brefs délais.")
                return redirect("core:contact")

            except Exception as e:
                # Log error server-side without leaking credentials or internal details
                logger.error("Échec de l'envoi de l'email de contact: %s", str(e))
                messages.error(
                    request,
                    "Une erreur technique est survenue lors de l'envoi de votre message. "
                    "Veuillez réessayer dans un instant ou m'écrire directement par email."
                )
                return render(request, "core/contact.html", {"form": form})
        else:
            messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")
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
