# MickaelCode.com — Refactoring Complet vers Django

Plateforme web full-stack professionnelle propulsée par **Python 3.12**, **Django 5.1**, **Django Templates**, **PostgreSQL** et **Stripe**.
Ce projet remplace l'ancien site statique / frontend JS par une architecture serveur robuste, ultra-performante pour le SEO, sécurisée et taillée pour monétiser des formations e-learning.

---

## 1. Architecture du Projet

L'application est structurée en 7 applications Django modulaires et découplées :

```text
MickaelCode/
├── config/                  # Configuration principale Django (settings, urls, wsgi)
├── core/                    # Pages publiques (Accueil, À propos, Réalisations, Compétences, Contact, Légal, SEO)
├── accounts/                # Modèle utilisateur personnalisé, authentification email/pseudo, profils, reset mdp
├── blog/                    # CMS de blog Markdown, rendu HTML assaini (Bleach), tags, catégories, temps de lecture
├── courses/                 # Catalogue e-learning, modules, leçons, paywall serveur, suivi de progression
├── billing/                 # Stripe Checkout, gestion idempotente des webhooks, commandes et droits d'accès
├── dashboard/               # Espace apprenant privé (vue d'ensemble, reprise de cours, historique, achats)
├── marketing/               # Newsletter RGPD, service Brevo / MailerLite, désinscription en 1 clic
├── static/                  # Fichiers statiques (CSS, JS, images, polices, animation canvas constellation)
├── templates/               # Templates HTML sémantiques (base.html, includes, vues spécifiques)
├── requirements.txt         # Dépendances Python verrouillées
├── .env.example             # Gabarit des variables d'environnement
├── Procfile & railway.json  # Configuration de déploiement en production
└── manage.py                # Point d'entrée des commandes CLI Django
```

---

## 2. Identité Visuelle & UX

L'identité visuelle historique de **MickaelCode** a été scrupuleusement préservée et sublimée :
- **Palette de couleurs** : Noir profond (`#000000`), Cyan électrique (`#00FFFF`), Corail / Tomate (`#ff6347`), nuances d'ardoise et blanc pur.
- **Typographie** : Polices Google Fonts *Righteous*, *Roboto*, *Lato* et *Sacramento*.
- **Canvas interactif** : Réseau de particules / constellation dynamique sur fond noir (`static/js/main.js`).
- **Responsive Design** : Menu hamburger coulissant fluide sur mobile et tablette, grilles CSS adaptatives.

---

## 3. Guide d'Installation Locale (Windows PowerShell)

### Prérequis
- Python 3.12 ou supérieur installé.
- PowerShell avec les droits d'exécution de scripts standard.

### Étape 1 : Créer et activer l'environnement virtuel
```powershell
# Cloner ou se positionner dans le dossier du projet
cd c:\Users\micka\Desktop\MickaelCode

# Créer le venv Python 3.12
py -3.12 -m venv .venv

# Activer le venv sous PowerShell
.\.venv\Scripts\Activate.ps1
```

### Étape 2 : Installer les dépendances
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 3 : Configurer les variables d'environnement
Copiez le gabarit `.env.example` vers un fichier `.env` local :
```powershell
Copy-Item .env.example .env
```
*(Le fichier `.env` est automatiquement ignoré par Git via `.gitignore`).*

### Étape 4 : Appliquer les migrations
```powershell
python manage.py migrate
```

### Étape 5 : Charger les données de démonstration réalistes
Une commande de seed dédiée peuple instantanément la base avec les compétences, les projets du portfolio, des articles de blog formatés en Markdown, un cursus complet de formation et des comptes de test :
```powershell
python manage.py seed_data
```

Comptes préconfigurés :
- **Super-administrateur** : `admin@mickaelcode.com` / `admin1234`
- **Compte apprenant test** : `apprenant@exemple.com` (pseudo : `apprenant`) / `student1234`

### Étape 6 : Démarrer le serveur de développement
```powershell
python manage.py runserver
```
Rendez-vous sur [http://127.0.0.1:8000/](http://127.0.0.1:8000/) dans votre navigateur.

---

## 4. Fonctionnalités Clés & Sécurité

### Authentification & Gestion des Comptes (`accounts`)
- Modèle `User` étendant `AbstractUser` créé dès la migration initiale.
- Connexion indifféremment par **adresse e-mail** ou **nom d'utilisateur**.
- Consentement RGPD pour la newsletter **distinct et facultatif** (non précoché).
- Flux complet de réinitialisation de mot de passe par e-mail avec templates dédiés.
- Espace de modification du profil avec upload d'avatar et gestion des préférences.

### Blog Technique Markdown (`blog`)
- Contenu source stocké sous forme brute Markdown dans la base de données.
- Rendu HTML sécurisé et assaini via **Bleach** (neutralisation de tout script XSS ou balise non autorisée).
- Calcul dynamique du temps de lecture estimé.
- Filtrage par catégorie, tags et recherche textuelle plein texte.
- Brouillons strictement inaccessibles au public (seuls les administrateurs connectés peuvent les prévisualiser).

### Catalogue & Lecteur de Formations (`courses`)
- Cursus structurés en Modules et Leçons vidéo.
- **Paywall côté serveur** : les leçons payantes renvoient une réponse HTTP `403 Forbidden` pour tout utilisateur non inscrit.
- Support des leçons gratuites ("Aperçu gratuit").
- Abstraction multi-fournisseurs vidéo (`courses/services.py`) pour intégrer facilement **Bunny Stream**, **Mux** ou des flux vidéo HTML5 privés sans exposer d'URL permanente non protégée.
- Enregistrement de la progression et mémorisation de la position de lecture (AJAX).

### Intégration Stripe & Webhooks Idempotents (`billing`)
- Flux sécurisé via **Stripe Checkout** : le prix est toujours récupéré en base de données côté serveur, jamais depuis le navigateur.
- Endpoint webhook `/billing/webhook/` validant la signature cryptographique (`STRIPE_WEBHOOK_SECRET`).
- Déblocage automatique et idempotent des formations : si un webhook est relivré plusieurs fois par Stripe, l'accès n'est débloqué qu'une seule fois sans erreur.
- Gestion des remboursements : révocation automatique du droit d'accès et notification de l'apprenant.

### Espace Personnel Apprenant (`dashboard`)
- Interface dédiée aux membres connectés, séparée de Django Admin.
- Vue d'ensemble avec bouton de reprise directe de lecture de la dernière leçon consultée.
- Suivi de la complétion pourcentage par formation.
- Historique d'achats, statuts de paiement et références de commande.
- Système de notifications internes (achats confirmés, cours débloqués).

### Newsletter & Campagnes Commerciales (`marketing`)
- Service d'intégration Python abstrait pour **Brevo** (ex-Sendinblue) et **MailerLite** (`marketing/services.py`).
- Enregistrement horodaté de la preuve de consentement et de l'IP du souscripteur.
- Lien de désinscription unique en 1 clic via jeton chiffré (`unsubscribe_token`).
- Action de synchronisation par lot directement intégrée dans l'interface d'administration Django.

### Administration Moderne (`Django Unfold`)
- Interface d'administration moderne basée sur **Django Unfold** aux couleurs de la marque MickaelCode.
- Tableaux de bord personnalisés affichant en temps réel les KPI : chiffre d'affaires total, nombre d'apprenants, formations publiées et abonnés newsletter.
- Édition confortable des contenus Markdown, filtres par statut et recherche instantanée.

---

## 5. Tests Automatisés

Le projet comprend une suite complète de 33 tests automatisés validant tous les cas critiques :
- Comptes (inscription, validation des CGU, login par email/pseudo, logout, reset mdp).
- Core (pages publiques, soumission du formulaire de contact, sitemaps, page 404).
- Blog (visibilité des articles publiés, protection des brouillons, assainissement HTML du Markdown).
- Formations (accès leçons gratuites, blocage des leçons payantes, validation de progression).
- Stripe (création de commande, webhook Checkout, idempotence, remboursement).
- Newsletter (consentement obligatoire, désinscription par jeton et par formulaire).

Pour exécuter les tests :
```powershell
python manage.py test
```

---

## 6. Déploiement en Production (Railway / PostgreSQL)

Le projet est configuré pour un déploiement continu sur **Railway** :
1. Connectez votre dépôt Git à Railway.
2. Ajoutez un plugin **PostgreSQL** dans votre projet Railway.
3. Configurez les variables d'environnement requises dans le dashboard Railway :
   - `SECRET_KEY` : une clé aléatoire forte.
   - `DEBUG` : `False`.
   - `ALLOWED_HOSTS` : `mickaelcode.com,*.railway.app`.
   - `DATABASE_URL` : injecté automatiquement par le plugin PostgreSQL de Railway.
   - `STRIPE_PUBLIC_KEY` & `STRIPE_SECRET_KEY` & `STRIPE_WEBHOOK_SECRET` : vos clés de production Stripe.
   - `BREVO_API_KEY` : votre clé API Brevo pour les e-mails.
4. Railway exécutera automatiquement la commande de déploiement définie dans `railway.json` :
   ```bash
   python manage.py migrate && python manage.py collectstatic --no-input && gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:$PORT
   ```
5. Le serveur de fichiers statiques **WhiteNoise** avec compression Brotli sert les fichiers sans nécessiter de serveur Nginx séparé.
