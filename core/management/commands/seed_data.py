from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from core.models import Skill, PortfolioProject
from blog.models import Category, Tag, Post
from courses.models import Course, Module, Lesson, Enrollment, LessonProgress
from billing.models import Order
from marketing.models import NewsletterSubscriber
from dashboard.models import StudentNotification


class Command(BaseCommand):
    help = "Seeds initial database with realistic projects, courses, skills, and demonstration users."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Admin User
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@mickaelcode.com",
                "first_name": "Mickael",
                "last_name": "Code",
                "is_staff": True,
                "is_superuser": True,
                "terms_accepted": True,
            }
        )
        if created:
            admin_user.set_password("admin1234")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin1234)"))

        # 2. Demo Student User
        student_user, created = User.objects.get_or_create(
            username="apprenant",
            defaults={
                "email": "apprenant@exemple.com",
                "first_name": "Alexandre",
                "last_name": "Dev",
                "terms_accepted": True,
                "newsletter_accepted": True,
                "newsletter_consent_date": timezone.now(),
            }
        )
        if created:
            student_user.set_password("student1234")
            student_user.save()
            self.stdout.write(self.style.SUCCESS("Created student user (apprenant / student1234)"))

        # 3. Skills
        skills_data = [
            ("Django & Python", 90, "backend", 1),
            ("Tailwind CSS", 80, "frontend", 2),
            ("PostgreSQL & ORM", 85, "backend", 3),
            ("Vue.js", 65, "frontend", 4),
            ("React.js", 60, "frontend", 5),
            ("Express.js & Node", 60, "backend", 6),
            ("Docker & Linux", 75, "devops", 7),
        ]
        for name, pct, cat, ord_num in skills_data:
            Skill.objects.get_or_create(
                name=name,
                defaults={"percentage": pct, "category": cat, "order": ord_num, "is_featured": True}
            )

        # 4. Portfolio Projects
        projects_data = [
            {
                "title": "Excel Workflow Automation",
                "slug": "excel-workflow",
                "client": "Industrie Logistique",
                "tagline": "Plateforme d'automatisation et de validation de flux tabulaires",
                "description": "Application Django sur-mesure permettant l'ingestion massive de fichiers Excel, le contrôle de cohérence métier en temps réel et la génération de rapports décisionnels. Réduction de 85% du temps de traitement manuel.",
                "technologies": "Django, Python, Pandas, OpenPyXL, Celery, PostgreSQL",
                "order": 1,
            },
            {
                "title": "Magenta E-commerce",
                "slug": "magenta-ecommerce",
                "client": "Marque Prêt-à-porter",
                "tagline": "Boutique en ligne haute performance avec checkout Stripe",
                "description": "Architecture e-commerce complète avec gestion des stocks en temps réel, passerelle Stripe Checkout sécurisée, emails transactionnels Brevo et tableau de bord de pilotage des ventes.",
                "technologies": "Django 5, Stripe, Tailwind CSS, Redis, PostgreSQL",
                "order": 2,
            },
            {
                "title": "Marseille Fight Club",
                "slug": "marseille-fight-club",
                "client": "Club Sportif",
                "tagline": "Plateforme de réservation de cours et gestion des adhésions",
                "description": "Portail web pour les adhérents : réservation de créneaux d'entraînement (MMA, Boxe, BJJ), gestion des plannings d'entraîneurs et suivi des abonnements récurrents.",
                "technologies": "Django, Python, Vanilla JS, CSS3, SQLite",
                "order": 3,
            },
            {
                "title": "Nestcase SaaS",
                "slug": "nestcase-saas",
                "client": "PropTech",
                "tagline": "SaaS de gestion locative et analytique immobilière",
                "description": "Application multi-tenant pour gestionnaires de parcs immobiliers. Tableaux de bord dynamiques, alertes d'échéances de baux et génération automatique de quittances.",
                "technologies": "Django, Vue.js, Tailwind, Chart.js, PostgreSQL",
                "order": 4,
            },
            {
                "title": "Pralinée Artisanat",
                "slug": "pralinee-artisanat",
                "client": "Chocolaterie Artisanale",
                "tagline": "Site vitrine et commandes personnalisées",
                "description": "Boutique gourmande avec click & collect, paiement en ligne sécurisé et expérience client mobile raffinée respectant la charte graphique de la marque.",
                "technologies": "Django, HTML5, CSS3, Stripe",
                "order": 5,
            },
            {
                "title": "VCar Mobility",
                "slug": "vcar-mobility",
                "client": "Mobilité Urbaine",
                "tagline": "Système de réservation de véhicules partagés",
                "description": "Application de géolocalisation et de réservation de flotte de véhicules avec gestion des cautions et facturation automatisée.",
                "technologies": "Django REST, Python, OpenStreetMap, PostgreSQL",
                "order": 6,
            },
        ]
        for p_data in projects_data:
            PortfolioProject.objects.get_or_create(slug=p_data["slug"], defaults=p_data)

        # 5. Blog Categories, Tags and Posts
        cat_django, _ = Category.objects.get_or_create(name="Django & Architecture", defaults={"slug": "django-architecture"})
        cat_sec, _ = Category.objects.get_or_create(name="Cybersécurité Web", defaults={"slug": "cybersecurite-web"})
        cat_perf, _ = Category.objects.get_or_create(name="Performance & Bases de Données", defaults={"slug": "performance-db"})

        tag_orm, _ = Tag.objects.get_or_create(name="ORM", defaults={"slug": "orm"})
        tag_sec, _ = Tag.objects.get_or_create(name="Sécurité", defaults={"slug": "securite"})
        tag_prod, _ = Tag.objects.get_or_create(name="Production", defaults={"slug": "production"})

        post_1, created = Post.objects.get_or_create(
            slug="pourquoi-choisir-django-pour-votre-saas",
            defaults={
                "title": "Pourquoi Choisir Django en 2026 pour Votre Prochain SaaS ?",
                "excerpt": "Alors que les stacks JavaScript se multiplient, Django demeure le framework le plus rentable pour expédier rapidement un SaaS fiable, sécurisé et maintenable.",
                "author": admin_user,
                "category": cat_django,
                "status": "published",
                "content_markdown": """## La Véritable Valeur de Django

Dans le paysage tech moderne, les équipes s'épuisent souvent à assembler des dizaines de micro-packages pour obtenir une simple authentification ou une gestion des sessions. Django adopte l'approche **"Batteries Included"**.

### 1. Sécurité Intégrée Dès le Jour 1

Django protège par défaut contre les vulnérabilités du top 10 OWASP :
- Protection **CSRF** native sur tous les formulaires.
- Échappement automatique dans les **templates** contre les failles XSS.
- Requêtes ORM paramétrées éliminant les **injections SQL**.

### 2. Le Modèle Utilisateur Personnalisé

La règle d'or pour tout projet SaaS est de déclarer immédiatement un `AbstractUser` :

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
```

### 3. Conclusion

Choisir Django, c'est choisir la prédictibilité, la rapidité de livraison et des nuits paisibles en production.""",
                "meta_title": "Pourquoi Choisir Django en 2026 pour Votre SaaS | MickaelCode",
                "meta_description": "Découvrez pourquoi Django reste le meilleur framework pour lancer un SaaS rentable et sécurisé.",
            }
        )
        if created:
            post_1.tags.add(tag_orm, tag_prod)

        post_2, created = Post.objects.get_or_create(
            slug="optimiser-les-performances-orm-django-requetes-n-plus-un",
            defaults={
                "title": "Maîtriser l'ORM Django : Éviter le Piège des Requêtes N+1",
                "excerpt": "Comment `select_related` et `prefetch_related` peuvent diviser par dix le temps de réponse de vos pages Django les plus chargées.",
                "author": admin_user,
                "category": cat_perf,
                "status": "published",
                "content_markdown": """## Le Problème du N+1 dans l'ORM

Lorsque vous itérez sur un QuerySet contenant des clés étrangères, chaque accès à la relation génère une nouvelle requête SQL si vous n'avez pas préchargé les données.

### Mauvaise pratique (N+1) :
```python
# 1 requête pour les commandes + 1 requête par commande pour le client !
orders = Order.objects.all()
for order in orders:
    print(order.user.email)
```

### Bonne pratique (`select_related`) :
```python
# 1 seule requête SQL avec jointure INNER JOIN
orders = Order.objects.select_related("user").all()
for order in orders:
    print(order.user.email)
```

Pour les relations Many-to-Many ou Many-to-One inversées, utilisez `prefetch_related()` pour minimiser les allers-retours avec PostgreSQL.""",
                "meta_title": "Éviter les Requêtes N+1 avec l'ORM Django | MickaelCode",
                "meta_description": "Guide pratique pour optimiser vos requêtes ORM Django avec select_related et prefetch_related.",
            }
        )
        if created:
            post_2.tags.add(tag_orm, tag_prod)

        # 6. Courses & Modules & Lessons
        course_1, _ = Course.objects.get_or_create(
            slug="formation-complete-django-5-production",
            defaults={
                "title": "Django 5 de A à Z : Développez et Déployez une Plateforme Web Complète",
                "short_description": "Apprenez à concevoir, structurer, sécuriser et déployer une véritable application SaaS avec Django 5, PostgreSQL et Stripe.",
                "description_markdown": """Cette formation pratique vous guide étape par étape dans la création d'une application professionnelle de production. Pas de code jetable, nous construisons un produit solide prêt à accueillir de vrais utilisateurs payants.""",
                "level": "intermediate",
                "price": Decimal("49.00"),
                "currency": "EUR",
                "status": "published",
                "is_featured": True,
                "learning_objectives": "Maîtriser l'architecture modulaire de Django\nConcevoir un modèle utilisateur personnalisé sécurisé\nIntégrer Stripe Checkout et les webhooks idempotents\nOptimiser l'ORM pour éviter les ralentissements\nDéployer sur Railway avec PostgreSQL et HTTPS",
                "prerequisites": "Bases du langage Python et notions fondamentales de HTML/CSS.",
            }
        )

        mod_1, _ = Module.objects.get_or_create(
            course=course_1,
            order=1,
            defaults={"title": "Fondations et Architecture Propre", "description": "Configuration du projet, venv et Custom User Model."}
        )
        Lesson.objects.get_or_create(
            module=mod_1,
            order=1,
            defaults={
                "title": "Introduction & Architecture du Projet",
                "duration_minutes": 12,
                "video_provider": "embed",
                "video_id_or_url": "sample_video_intro",
                "is_free_preview": True,
                "status": "published",
                "description": "Présentation des objectifs du cours et installation des prérequis.",
            }
        )
        Lesson.objects.get_or_create(
            module=mod_1,
            order=2,
            defaults={
                "title": "Création du Modèle Utilisateur Personnalisé",
                "duration_minutes": 18,
                "video_provider": "embed",
                "video_id_or_url": "sample_video_auth",
                "is_free_preview": False,
                "status": "published",
                "description": "Pourquoi et comment étendre AbstractUser avant les premières migrations.",
            }
        )

        mod_2, _ = Module.objects.get_or_create(
            course=course_1,
            order=2,
            defaults={"title": "Monétisation et Paiements Stripe", "description": "Sessions Checkout, webhooks et déblocage sécurisé."}
        )
        Lesson.objects.get_or_create(
            module=mod_2,
            order=1,
            defaults={
                "title": "Intégration de Stripe Checkout",
                "duration_minutes": 22,
                "video_provider": "embed",
                "video_id_or_url": "sample_video_stripe",
                "is_free_preview": False,
                "status": "published",
                "description": "Création de la session de paiement sécurisée côté serveur.",
            }
        )

        # 7. Grant access to demo student user
        enr, _ = Enrollment.objects.get_or_create(
            user=student_user,
            course=course_1,
            defaults={"status": "active", "acquisition_source": "demo_seed"}
        )
        lesson_first = course_1.first_lesson()
        if lesson_first:
            LessonProgress.objects.get_or_create(
                user=student_user,
                lesson=lesson_first,
                defaults={"is_completed": True, "completed_at": timezone.now()}
            )

        Order.objects.get_or_create(
            user=student_user,
            course=course_1,
            defaults={
                "amount": course_1.price,
                "currency": course_1.currency,
                "status": "completed",
                "stripe_checkout_session_id": "cs_test_seed_demo",
            }
        )

        # 8. Newsletter subscriber demo
        NewsletterSubscriber.objects.get_or_create(
            email="abonne@exemple.com",
            defaults={
                "first_name": "Julien",
                "consent_given": True,
                "consent_timestamp": timezone.now(),
                "source": "homepage_footer",
                "status": "subscribed",
                "is_synced": True,
            }
        )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with realistic data!"))
