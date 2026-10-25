# RAPPORT DE CORRECTIONS PRÉ-PRODUCTION — PLATEFORME MICKAELCODE (DJANGO 5.1)

> **Document de traçabilité des corrections techniques et guide de déploiement**  
> **Date de réalisation :** 25 octobre 2026  
> **Auteur des interventions :** Antigravity AI (Pair Programming Senior Python / Django)  
> **Statut global :** Bloqueurs P0 résolus, suite de tests étendue (48/48 succès), projet prêt pour déploiement  
> **Fichier de référence :** `RAPPORT_CORRECTIONS_PRE_PRODUCTION.md`

---

## 1. Synthèse des interventions et état des bloqueurs P0

Les trois bloqueurs critiques identifiés lors de l'audit pré-production initial ont été intégralement traités et validés localement :

| Bloqueur P0 | Problème initial constaté | Solution technique implémentée | État |
|---|---|---|---|
| **P0 n° 1 : Tailwind CSS & Fichiers statiques** | `package.json`, `tailwind.config.js` et le fichier compilé `static/css/tailwind.css` étaient non trackés par Git (`untracked`). Sur Railway, le site aurait été déployé sans feuille de style ou avec un échec de build. | 1. Compilation minifiée du CSS avec Tailwind CLI (`60 Ko`).<br>2. Création d'un fichier de build multi-étapes `nixpacks.toml` combinant Python 3.12 et Node.js 20.<br>3. Découplage de `collectstatic` hors du `startCommand` pour une compilation au moment du build.<br>4. Ajustement de `.gitignore` pour versionner `package-lock.json`. | ✅ **Corrigé & Validé** |
| **P0 n° 2 : Stockage média persistant (Cloudflare R2)** | Les uploads reposaient sur `FileSystemStorage` dans le répertoire local `/media/`. Sur conteneur Railway éphémère, chaque déploiement aurait détruit les avatars utilisateurs et les couvertures de cours. | 1. Installation et déclaration de `django-storages[s3]` et `boto3`.<br>2. Configuration dynamique de `STORAGES["default"]` dans `settings.py` pilotée par variables d'environnement (`USE_R2`, `R2_ACCESS_KEY_ID`, etc.).<br>3. Fallback transparent et gracieux vers `FileSystemStorage` en local/tests.<br>4. Adaptation aux spécificités de Cloudflare R2 (`default_acl = None`, `signature_version = "s3v4"`). | ✅ **Corrigé & Validé** |
| **P0 n° 3 : Bunny Stream Token Auth & Reprise de lecture** | L'iframe Bunny Stream exposait l'ID vidéo sans jeton d'authentification cryptographique. L'endpoint AJAX `/courses/progress/<id>/position/` existait mais n'était pas synchronisé par le frontend. | 1. Implémentation de la signature HMAC SHA-256 Bunny Stream dans `VideoPlayerService.generate_bunny_signed_url`.<br>2. Contrôle d'accès serveur obligatoire avant la génération de jeton.<br>3. Intégration du SDK Player.js de Bunny Stream dans `lesson_player.html`.<br>4. Écoute des événements `timeupdate` (throttled à 15s), `pause` et `ended` avec reprise automatique au timestamp sauvegardé.<br>5. Validation stricte des bornes temporelles sur le serveur. | ✅ **Corrigé & Validé** |

---

## 2. Inventaire des fichiers modifiés et créés

### 2.1 Nouveaux fichiers créés
1. **`nixpacks.toml`** : Configuration déclarative du build multi-langages Railway (phases setup, install, build avec compilation CSS et collectstatic, commande de démarrage Gunicorn).
2. **`RAPPORT_CORRECTIONS_PRE_PRODUCTION.md`** : Ce document exhaustif de référence.

### 2.2 Fichiers modifiés
1. **`config/settings.py`** :
   - Ajout de `"storages"` dans `INSTALLED_APPS`.
   - Ajout du garde-fou de sécurité levant une `ValueError` en production si `DEBUG=False` et `SECRET_KEY` est absente ou insecure.
   - Configuration du stockage `STORAGES["default"]` pour Cloudflare R2 avec fallback local sur `FileSystemStorage`.
   - Calcul dynamique de `MEDIA_URL` pointant vers le domaine CDN R2 lorsque configuré.
2. **`courses/services.py`** :
   - Implémentation de `generate_bunny_signed_url` respectant l'algorithme officiel Bunny Token Authentication (concaténation `TokenSecurityKey + VideoID + Expires` condensée en hexadécimal SHA-256).
   - Ajout du paramètre `user` dans `render_player` avec blocage strict côté serveur si `not lesson.can_access(user)`.
3. **`courses/views.py`** :
   - Passage de `request.user` au service `VideoPlayerService.render_player`.
   - Assainissement et validation des bornes temporelles dans `save_video_position_view` (vérification `seconds >= 0` et plafonnement à `durée_leçon + marge`).
4. **`templates/courses/lesson_player.html`** :
   - Inclusion du SDK `player-0.1.0.min.js` de Bunny Stream.
   - Contrôleur JavaScript Vanilla pour la synchronisation de la position de lecture (throttling à 15 secondes, sauvegarde forcée sur pause et fin de lecture).
   - Repositionnement automatique du lecteur au chargement (`setCurrentTime`).
   - Marque de fin de cours déclenchée à l'événement `ended`.
   - Bascule de complétion de leçon sans rechargement de page via AJAX.
5. **`accounts/views.py`** :
   - Décoration de `login_view` avec `@ratelimit(key="ip", rate="10/m", method=["POST"], block=False)`.
   - Interception du dépassement de quota et retour d'un statut HTTP 429 avec message convivial.
6. **`core/management/commands/seed_data.py`** :
   - Ajout d'un contrôle bloquant l'exécution de la commande de démonstration si `DEBUG=False`, empêchant toute injection d'utilisateurs de test en production.
7. **`railway.json`** :
   - Nettoyage du `startCommand` pour ne lancer que Gunicorn au démarrage (la collecte statique étant désormais prise en charge au build par Nixpacks).
8. **`requirements.txt`** :
   - Ajout de `django-storages[s3]>=1.14.4`, `boto3>=1.35.0` et `django-ratelimit>=4.1.0`.
9. **`.gitignore`** :
   - Retrait de `package-lock.json` des fichiers ignorés pour garantir l'exactitude des versions NPM lors du build Railway.
10. **`.env.example`** :
    - Documentation exhaustive des variables d'environnement Cloudflare R2, Bunny Stream, Brevo, Stripe et Django Core.
11. **`courses/tests.py`** :
    - 6 nouveaux tests unitaires couvrant l'algorithme de hachage Bunny, la génération de player signé, le blocage des utilisateurs non autorisés et la validation de l'endpoint de positionnement.
12. **`accounts/tests.py`** :
    - Isolation du cache de rate-limiting (`cache.clear()`) et test unitaire validant le blocage HTTP 429 après 10 tentatives échouées.
13. **`core/tests.py`** :
    - Tests unitaires validant le fallback du stockage, la résolution de `MEDIA_URL` et le garde-fou sur la `SECRET_KEY`.

---

## 3. Résultats des tests et preuves d'exécution

### 3.1 Suite complète de tests automatisés Django
La suite de tests a été exécutée sur l'environnement local après l'ensemble des modifications :

```text
Creating test database for alias 'default'...
Found 48 test(s).
System check identified no issues (0 silenced).
................................................
----------------------------------------------------------------------
Ran 48 tests in 48.876s

OK
Destroying test database for alias 'default'...
```

* **Résultat initial avant mission :** 38 tests réussis.
* **Résultat final après corrections :** **48 tests réussis (100% de succès, 0 échec, 0 régression)**.

### 3.2 Détail des 10 nouveaux tests ajoutés

| Fichier de test | Nom du test | Comportement vérifié | Résultat |
|---|---|---|---|
| `courses/tests.py` | `test_bunny_token_generation_algorithm` | Validité de la formule mathématique SHA-256 (`token_key + video_id + expires`). | **SUCCÈS** |
| `courses/tests.py` | `test_bunny_player_renders_token_when_authorized` | Injection correcte du token et de la date d'expiration dans l'iframe Bunny pour un utilisateur inscrit. | **SUCCÈS** |
| `courses/tests.py` | `test_bunny_player_blocks_unauthorized_user` | Remplacement de l'iframe par un message d'accès réservé pour les utilisateurs non inscrits. | **SUCCÈS** |
| `courses/tests.py` | `test_save_video_position_endpoint` | Persistance correcte du timestamp dans `LessonProgress.last_position_seconds`. | **SUCCÈS** |
| `courses/tests.py` | `test_save_video_position_bounds_sanitization` | Assainissement des valeurs négatives (remises à 0) et plafonnement des valeurs anormales. | **SUCCÈS** |
| `courses/tests.py` | `test_save_video_position_unauthorized_rejected` | Renvoi d'un statut HTTP 403 Forbidden si un non-inscrit tente d'appeler l'API de progression. | **SUCCÈS** |
| `accounts/tests.py` | `test_login_rate_limiting_triggers_429` | Déclenchement effectif du code HTTP 429 après 10 requêtes POST rapides sur la connexion. | **SUCCÈS** |
| `core/tests.py` | `test_default_storage_fallback_to_filesystem` | Garantie que le stockage par défaut reste `FileSystemStorage` en l'absence de variables R2. | **SUCCÈS** |
| `core/tests.py` | `test_storage_media_url_configuration` | Vérification de la conformité du préfixe d'URL des médias. | **SUCCÈS** |
| `core/tests.py` | `test_production_secret_key_security_guard` | Déclenchement d'une exception fatale en cas de clé insecure avec `DEBUG=False`. | **SUCCÈS** |

### 3.3 Contrôle système Django
La commande `python manage.py check` confirme :
```text
System check identified no issues (0 silenced).
```

---

## 4. Configuration de production et inventaire des variables d'environnement

Le tableau ci-dessous dresse l'inventaire complet des variables d'environnement nécessaires au fonctionnement de la plateforme en production sur Railway.

> ⚠️ **Sécurité :** Aucune valeur secrète n'est exposée ci-dessous. Les valeurs doivent être injectées dans l'interface Railway (onglet *Variables*).

| Variable d'environnement | Utilité métier | Caractère | Service concerné | Statut / Valeur recommandée |
|---|---|---|---|---|
| `DEBUG` | Désactive le mode debug et active les en-têtes de sécurité HTTPS stricts. | **Obligatoire** | Railway Web | `False` |
| `SECRET_KEY` | Clé maîtresse cryptographique de chiffrement des sessions et tokens. | **Obligatoire** | Railway Web | À générer (50+ caractères aléatoires) |
| `ALLOWED_HOSTS` | Liste des noms d'hôtes autorisés à joindre le serveur Django. | **Obligatoire** | Railway Web | `mickaelcode.com,www.mickaelcode.com,*.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | Origines autorisées pour les requêtes POST (formulaires et Stripe). | **Obligatoire** | Railway Web | `https://mickaelcode.com,https://www.mickaelcode.com,https://*.railway.app` |
| `SITE_URL` | URL racine publique du site (utilisée pour les retours Stripe et e-mails). | **Obligatoire** | Railway Web | `https://mickaelcode.com` |
| `DATABASE_URL` | Chaîne de connexion PostgreSQL. | **Obligatoire** | Railway Database | Fournie automatiquement par le plugin PostgreSQL Railway |
| `USE_R2` | Active l'utilisation du backend de stockage Cloudflare R2 pour les médias. | **Obligatoire** | Railway Web | `True` |
| `R2_ACCESS_KEY_ID` | Identifiant de la clé d'accès API Cloudflare R2. | **Obligatoire** | Cloudflare R2 | À copier depuis le tableau de bord Cloudflare |
| `R2_SECRET_ACCESS_KEY` | Clé secrète associée au token d'accès R2. | **Obligatoire** | Cloudflare R2 | À copier depuis le tableau de bord Cloudflare |
| `R2_BUCKET_NAME` | Nom du bucket de stockage des fichiers médias. | **Obligatoire** | Cloudflare R2 | `mickaelcode-media` |
| `R2_ENDPOINT_URL` | Point de terminaison S3 de votre compte Cloudflare. | **Obligatoire** | Cloudflare R2 | `https://<votre_account_id>.r2.cloudflarestorage.com` |
| `R2_CUSTOM_DOMAIN` | Domaine personnalisé pour servir les images en CDN rapide. | Recommandé | Cloudflare R2 | `media.mickaelcode.com` (ou URL `pub-xxx.r2.dev`) |
| `VIDEO_PROVIDER` | Fournisseur de streaming vidéo utilisé par la plateforme. | **Obligatoire** | Railway Web | `bunny` |
| `BUNNY_STREAM_LIBRARY_ID` | Identifiant numérique de la vidéothèque Bunny Stream. | **Obligatoire** | Bunny Stream | Disponible dans *Bunny Dashboard > Stream* |
| `BUNNY_STREAM_TOKEN_KEY` | Clé de signature secrète pour générer les tokens vidéo HMAC. | **Obligatoire** | Bunny Stream | Disponible dans *Library > Security > Token Authentication* |
| `BUNNY_STREAM_API_KEY` | Clé API principale de gestion de la vidéothèque Bunny. | Recommandé | Bunny Stream | Disponible dans *Library > API* |
| `STRIPE_PUBLIC_KEY` | Clé publiable Stripe utilisée côté navigateur. | **Obligatoire** | Stripe | `pk_live_...` |
| `STRIPE_SECRET_KEY` | Clé secrète Stripe pour initialiser les sessions Checkout. | **Obligatoire** | Stripe | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Secret de signature du webhook pour valider les paiements. | **Obligatoire** | Stripe | `whsec_...` (créé lors de l'enregistrement de l'URL webhook) |
| `EMAIL_BACKEND` | Moteur d'expédition des e-mails Django. | **Obligatoire** | Railway Web | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | Hôte du serveur SMTP transactionnel. | **Obligatoire** | Brevo | `smtp-relay.brevo.com` |
| `EMAIL_PORT` | Port sécurisé TLS. | **Obligatoire** | Brevo | `587` |
| `EMAIL_USE_TLS` | Activation du protocole de chiffrement TLS. | **Obligatoire** | Brevo | `True` |
| `EMAIL_HOST_USER` | Identifiant de connexion SMTP Brevo. | **Obligatoire** | Brevo | Votre identifiant SMTP Brevo |
| `EMAIL_HOST_PASSWORD` | Clé SMTP Brevo. | **Obligatoire** | Brevo | Votre clé SMTP Brevo |
| `DEFAULT_FROM_EMAIL` | Adresse d'expédition visible par les clients. | **Obligatoire** | Railway Web | `MickaelCode <contact@mickaelcode.com>` |
| `CONTACT_EMAIL` | Adresse de réception des messages du formulaire de contact. | **Obligatoire** | Railway Web | `contact@mickaelcode.com` |
| `NEWSLETTER_PROVIDER` | Moteur de synchronisation de la newsletter. | **Obligatoire** | Railway Web | `brevo` |
| `BREVO_API_KEY` | Clé API v3 pour synchroniser les contacts newsletter. | **Obligatoire** | Brevo | `xkeysib-...` |
| `BREVO_LIST_ID` | Numéro de la liste de contacts cible dans Brevo. | **Obligatoire** | Brevo | `2` (identifiant de votre liste) |

---

## 5. Plan de déploiement final et checklist exécutable

Voici la procédure opérationnelle détaillée à suivre pour déployer la plateforme en production sur Railway sans risque d'erreur ou d'interruption de service.

### Étape 1 : Préparation du dépôt Git (Local)
1. **Compiler la dernière version des styles Tailwind :**
   ```powershell
   npm run build:css
   ```
2. **Tester la collecte des fichiers statiques :**
   ```powershell
   python manage.py collectstatic --no-input
   ```
3. **Vérifier l'état Git et ajouter les fichiers nécessaires :**
   ```powershell
   git add package.json package-lock.json tailwind.config.js postcss.config.js nixpacks.toml static_src/ static/css/tailwind.css
   git add config/ courses/ accounts/ core/ templates/ railway.json requirements.txt .gitignore .env.example
   git commit -m "fix(prod): resolve P0 blockers - Tailwind assets, Cloudflare R2 storage, Bunny Stream token auth and rate limiting"
   ```
4. **Pousser la branche vers le dépôt distant (GitHub/GitLab) :**
   ```powershell
   git push origin master
   ```

---

### Étape 2 : Configuration de l'infrastructure Railway
1. **Créer le projet Railway et connecter le dépôt Git.**
2. **Ajouter un service PostgreSQL :**
   - Cliquer sur *New > Database > Add PostgreSQL*.
   - Railway injecte automatiquement la variable `DATABASE_URL` dans le projet.
3. **Renseigner les variables d'environnement dans Railway :**
   - Se rendre sur le service web Django > *Variables*.
   - Renseigner l'ensemble des variables répertoriées au tableau de la section 4.

---

### Étape 3 : Initialisation de la base de données PostgreSQL
1. **Exécuter les migrations initiales sur la base de données distante :**
   *Depuis votre terminal local avec le CLI Railway :*
   ```bash
   railway run python manage.py migrate
   ```
   *(Cette commande applique toutes les migrations sur PostgreSQL sans verrouiller le serveur web).*
2. **Créer le premier compte Super-Administrateur de production :**
   ```bash
   railway run python manage.py createsuperuser
   ```
   *(Renseignez de manière interactive votre adresse e-mail et un mot de passe fort sans l'exposer dans les journaux).*
3. **Migration optionnelle des données initiales (articles, compétences, projets) :**
   Si vous souhaitez charger les données initiales de démonstration sur votre base de production :
   ```bash
   # Export depuis le poste local (SQLite)
   python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission -o datadump.json
   
   # Import vers PostgreSQL Railway
   railway run python manage.py loaddata datadump.json
   ```

---

### Étape 4 : Configuration des services externes
1. **Stripe :**
   - Dans le tableau de bord Stripe (*Développeurs > Webhooks*), ajouter l'endpoint de production :
     `https://mickaelcode.com/billing/webhook/`
   - Sélectionner les événements : `checkout.session.completed` et `charge.refunded`.
   - Copier la clé secrète de signature (`whsec_...`) et la renseigner dans la variable Railway `STRIPE_WEBHOOK_SECRET`.
2. **Bunny Stream :**
   - Dans la vidéothèque Bunny Stream > *Security*, activer **Token Authentication**.
   - Copier la clé de token et la renseigner dans `BUNNY_STREAM_TOKEN_KEY`.
   - Configurer les **Allowed Referrers** : `mickaelcode.com`, `www.mickaelcode.com`.
3. **Cloudflare R2 :**
   - Créer un bucket nommé `mickaelcode-media`.
   - Activer un domaine personnalisé (ex: `media.mickaelcode.com`) ou autoriser l'accès public en lecture.
   - Générer un token API R2 avec les droits *Admin Read & Write* et renseigner `R2_ACCESS_KEY_ID` et `R2_SECRET_ACCESS_KEY` dans Railway.

---

### Étape 5 : Tests de recette en production (Checklist post-déploiement)
- [ ] La page d'accueil (`https://mickaelcode.com/`) se charge avec les styles Tailwind et la typographie Righteous/Lato.
- [ ] La connexion à l'administration (`https://mickaelcode.com/admin/`) fonctionne avec le thème Unfold et les KPIs en direct.
- [ ] L'inscription d'un nouvel utilisateur crée bien un compte apprenant et le redirige vers le tableau de bord.
- [ ] L'achat d'un cours en mode test Stripe redirige vers Stripe Checkout et débloque instantanément la formation après confirmation webhook.
- [ ] La leçon vidéo s'affiche dans l'iframe sécurisée Bunny Stream avec son token cryptographique.
- [ ] La reprise de lecture mémorise la position de visionnage lors de la mise en pause.
- [ ] Le formulaire de contact expédie un e-mail à l'administrateur sans erreur 500.
- [ ] L'inscription à la newsletter enregistre la date et l'IP, et le lien de désinscription en 1 clic fonctionne.

---

## 6. Classification finale de l'état de préparation

| Composant | Catégorie de préparation | Commentaire de validation |
|---|---|---|
| **Compilation CSS Tailwind & Assets** | **Corrigé et testé localement** | Minifié à 60 Ko, `nixpacks.toml` prêt, `collectstatic` validé sans erreur. |
| **Authentification & Rate Limiting** | **Corrigé et testé localement** | Modèle User personnalisé, connexion email/pseudo, blocage force brute HTTP 429 validé par test. |
| **Sécurité du lecteur vidéo Bunny** | **Corrigé et testé localement** | Algorithme SHA-256 implémenté et testé unitairement. En attente de la clé Bunny de production. |
| **Synchronisation de la progression vidéo** | **Corrigé et testé localement** | SDK Player.js intégré, sauvegarde throttlée et validation serveur des timestamps en place. |
| **Passerelle de paiement Stripe** | **Corrigé et testé localement** | Checkout sessions, validation de signature webhook, idempotence et remboursements validés par tests. |
| **Stockage média Cloudflare R2** | **Corrigé mais nécessitant un test externe** | Code et fallback local validés par tests. Nécessite la création du bucket R2 et l'injection des clés. |
| **Expédition d'e-mails & Brevo** | **En attente de configuration** | Code fonctionnel (mock local actif). Nécessite la saisie des identifiants SMTP de production dans Railway. |
| **Base de données PostgreSQL** | **En attente de configuration** | `dj-database-url` et `psycopg2-binary` prêts. Nécessite le provisionnement du plugin Railway. |
| **Déploiement public Railway** | **Prêt — En attente de validation utilisateur** | Tous les prérequis techniques sont remplis. Arrêt volontaire avant mise en ligne. |

---

*Fin du rapport de corrections techniques pré-production — Projet Django 5.1 prêt pour mise en production sur Railway.*
