
# TournamentMaker

**TournamentMaker** est une application web développée avec **Django**. Elle permet de **créer**, **gérer** et **suivre facilement des tournois sportifs**, quels que soient le sport (football, basketball, handball, rugby, etc.).

Ce projet a été réalisé dans le cadre de notre projet de 3ᵉ année à l’ESIEE, présenté lors de la Journée des Projets du 26 juin 2025. Il a été conçu pour mettre en pratique nos compétences en développement web, en gestion de version avec Git, ainsi qu’en travail collaboratif.

## Utilisateurs ciblés

Notre plateforme s’adresse à **deux types de profils** :

1.  **Organisateurs**
   - Créent et planifient leurs propres tournois
   - Ajoutent des équipes et joueurs
   - Gèrent les matchs, scores, et classements

2.  **Joueurs et spectateurs**
   - Consultent les informations du tournoi (planning, résultats, scores)
   - Suivent l’évolution des équipes en temps réel
   - Peuvent visualiser le classement général et les matchs à venir

---

## Fonctionnalités principales

- Création de tournois personnalisés
- Ajout et gestion d’équipes ou de joueurs
- Génération automatique des rencontres
- Mise à jour des scores en direct
- Visualisation des classements et calendriers
- Interface administrateur sécurisée

---

##  Technologies utilisées

- [Python](https://www.python.org) – Langage principal
- [Django](https://www.djangoproject.com) – Framework web back-end
- [HTML](https://developer.mozilla.org/fr/docs/Web/HTML) – Structure des pages
- [CSS](https://developer.mozilla.org/fr/docs/Web/CSS) – Mise en forme
- [JavaScript](https://developer.mozilla.org/fr/docs/Web/JavaScript) – Interactivité (optionnel/à étendre)

> **Branche principale de développement** : `dev`

---

## User Guide

### Prérequis

- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)
- Git

### Étapes d’installation

1. **Cloner le projet :**
   ```bash
   git clone https://github.com/LouisAyzac/TournamentMaker.git
   cd TournamentMaker/TournoiApp
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Préparer la base de données :**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Lancer le serveur de développement :**
   ```bash
   python manage.py runserver
   ```

5. **Accéder à l’application :**
   [http://127.0.0.1:8000/TournamentMaker/](http://127.0.0.1:8000/TournamentMaker/)

---

### Interface d’administration Django

1. Créer un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```

2. Se connecter à l'admin :
   [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---


---

### Détail des commandes utilisées

Voici une explication détaillée de chaque commande utilisée lors de l’installation et du lancement de l’application :

#### Clonage du dépôt
```bash
git clone https://github.com/LouisAyzac/TournamentMaker.git
```
> Clone le projet depuis GitHub dans un dossier local nommé `TournamentMaker`.

```bash
cd TournamentMaker/TournoiApp
```
> Se déplace dans le dossier contenant le cœur de l’application Django.

#### Installation des dépendances
```bash
pip install -r requirements.txt
```
> Installe toutes les bibliothèques Python listées dans le fichier `requirements.txt` (ex: Django, certifi, etc.). Cela garantit que le projet dispose de tout le nécessaire pour fonctionner.

#### Migrations de la base de données
```bash
python manage.py makemigrations
```
> Génère les fichiers de migration à partir des modèles définis dans `models.py`. Ces fichiers décrivent les changements à apporter à la base de données (tables, champs, relations...).

```bash
python manage.py migrate
```
> Applique les migrations à la base de données SQLite. Cela crée les tables et les structures nécessaires pour faire fonctionner l’application.

#### Lancement du serveur de développement
```bash
python manage.py runserver
```
> Lance le serveur web intégré de Django, accessible à l’adresse [http://127.0.0.1:8000](http://127.0.0.1:8000). Idéal pour tester localement.

#### Création d’un superutilisateur
```bash
python manage.py createsuperuser
```
> Lance une procédure pour créer un compte administrateur. Ce compte permet de se connecter à l’interface d’administration Django à [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

---

Ces commandes sont toutes exécutées via la console ou le terminal. Elles sont essentielles pour faire fonctionner tout projet Django correctement.

---

### Gestion des organisateurs et accès sécurisé

Lors de la **création d’un tournoi**, un **email** est demandé : il s’agit de l’adresse email de l’organisateur du tournoi.

Voici comment fonctionne l’accès sécurisé :

1.  **Envoi automatique d’un email** :
   - Un email est envoyé à l’organisateur contenant un **lien pour définir son mot de passe**.
   - Ce mot de passe est strictement personnel et confidentiel.

2.  **Utilisation du compte organisateur** :
   - Ce compte permet à l’organisateur de :
     -  **Mettre à jour les scores** de toutes les équipes de son tournoi
     -  **Créer les phases finales** (playoffs, demi-finales, etc.)
   - À chaque action sensible (comme changer un score ou accéder aux phases finales), le **login et mot de passe** de l’organisateur sont demandés.

Cette fonctionnalité garantit que **seuls les organisateurs autorisés** peuvent modifier les éléments critiques d’un tournoi.


---

### Gestion des capitaines d’équipes

Lors de l’**inscription d’une équipe** à un tournoi, une adresse email est demandée au **capitaine** de l’équipe.

Voici comment cela fonctionne :

1.  **Envoi automatique d’un email au capitaine** :
   - Un lien de création de mot de passe est envoyé à l’adresse fournie.
   - Ce mot de passe permet au capitaine d’accéder à une interface sécurisée dédiée.

2.  **Accès restreint pour les capitaines** :
   - Chaque capitaine peut uniquement :
     -  **Mettre à jour les scores** de **son équipe uniquement**
   - Il n’a pas accès aux autres données du tournoi ni aux équipes adverses.

3.  **Authentification obligatoire** :
   - Pour modifier le score de son équipe, le capitaine doit **s’authentifier** avec son email et mot de passe personnel.

Cela permet de responsabiliser les capitaines tout en assurant un contrôle précis et sécurisé des modifications autorisées.

---


##  Architecture du projet / Developper Guide

```plaintext
TournamentMaker/
├── manage.py
├── db.sqlite3
├── README.md
│
├── TournioApp/                   
│   ├── admin.py                  
│   ├── models.py                 
│   ├── views.py                  
│   ├── urls.py                   
│   ├── templates/                 
│   ├── static/                  
│   ├── migrations/               
│   └── ...
│
├── TournoiApp/                    
│   ├── settings.py              
│   ├── urls.py                    
│   └── ...
```


---

### Détail de l’architecture du projet

Voici une description des principaux fichiers et dossiers de l'application :

```plaintext
TournamentMaker/
├── manage.py
```
> Fichier principal pour interagir avec le projet Django (lancer le serveur, exécuter les migrations, etc.).

```plaintext
├── db.sqlite3
```
> Base de données SQLite par défaut. Contient toutes les données persistantes (équipes, matchs, utilisateurs...).

```plaintext
├── README.md
```
> Documentation du projet, contenant toutes les informations utiles pour installation, usage et développement.

```plaintext
├── TournioApp/
```
> Application Django principale. Contient toute la logique métier et les composants spécifiques du tournoi.

- `admin.py` : Enregistre les modèles dans l’interface d’administration Django.
- `models.py` : Définit les classes représentant les données (équipes, tournois, matchs...).
- `views.py` : Contient les fonctions ou classes qui déterminent ce que renvoie chaque page.
- `urls.py` : Définit les routes internes à l’application.
- `templates/` : Contient les fichiers HTML rendus par Django.
- `static/` : Contient les fichiers statiques (CSS, JavaScript, images).
- `migrations/` : Historique des modifications du schéma de la base de données.

```plaintext
├── TournoiApp/
```
> Dossier de configuration global du projet Django.

- `settings.py` : Paramètres généraux (apps, middleware, base de données, chemins statiques...).
- `urls.py` : Point d’entrée des URLs du projet (peut inclure celles de `TournioApp`).
- `asgi.py` / `wsgi.py` : Interfaces pour déployer le projet sur un serveur web.



---

## Bonnes pratiques & conseils

- Utilisez des **branches** pour développer de nouvelles fonctionnalités
- Faites des **commits réguliers** avec des messages clairs
- Testez localement avant de fusionner vos PR

---


## Améliorations futures

- Ajout d’un système d’authentification utilisateurs (joueurs / visiteurs)
- Interface responsive pour mobile
- Notifications en temps réel (WebSocket ou polling)
- Export des données (PDF, CSV)
- Modularisation du projet (création de nouvelle app affin que notre projet soit mieux strucuré
- Stockage de la secret key

---

## Équipe projet

- **Ange Gagnard** 
- **Pablo Minelian**
- **Florian Garcia--Salon** 
- **Antoine Huang** 
- **Louis Ayzac** 
- **Rémy Abdoul Mazidou** 


