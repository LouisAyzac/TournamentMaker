# 🏆 TournamentMaker

**TournamentMaker** est une application web développée avec **Django**. Elle permet de **créer**, **gérer** et **suivre facilement des tournois sportifs** tels que le football, le rugby, le basketball ou le handball. Ce projet a été réalisé dans un cadre pédagogique afin de renforcer nos compétences en développement web, en gestion de version avec Git, et en travail d’équipe.

---


## 👥 Membres du projet

- **Ange Gagnard** – [Visualisation Git avec D3.js](https://onlywei.github.io/explain-git-with-d3/)
- **Pablo Minelian** – [Jeu pédagogique Git](https://ohmygit.org)
- **Florian Garcia--Salon** – [Cours OpenClassrooms : Git & GitHub](https://openclassrooms.com/fr/courses/7162856-gerez-du-code-avec-git-et-github)
- **Antoine Huang** – [Git for Computer Scientists](https://eagain.net/articles/git-for-computer-scientists/)
- **Louis Ayzac** – [Conférence Git (YouTube)](https://youtube.com/watch?v=1ffBJ4sVUb4&t=125s)
- **Rémy Adboul Mazidou** – [AgriponGit – Visualiseur Git](https://agripongit.vincenttunru.com/)

---

## 🛠️ Technologies utilisées

- [Python](https://docs.python.org) – Langage de programmation
- [Django](https://www.djangoproject.com) – Framework web back-end
- [HTML](https://developer.mozilla.org/fr/docs/Web/HTML) – Structure des pages
- [CSS](https://developer.mozilla.org/fr/docs/Web/CSS) – Mise en forme et design

> **Branche principale de développement** : `dev`

---

## ✨ Fonctionnalités principales

- Création de tournois personnalisés
- Ajout de joueurs ou d’équipes
- Génération automatique des matchs
- Suivi des scores et des résultats
- Tableau d’administration sécurisé

---

## 👤 User Guide

### 🔧 Installation de Django

#### Prérequis

- **Python 3.8** ou plus récent  
- **pip** (installé avec Python)  

#### Étapes d’installation

1. Vérifier que Python est installé :
    ```bash
    python --version
    ```

2. Mettre à jour `pip` :
    ```bash
    pip install --upgrade pip
    ```

3. Installer Django :
    ```bash
    pip install django
    ```

4. Vérifier que Django est bien installé :
    ```bash
    django-admin --version
    ```

---

### 🚀 Lancement du site web

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/LouisAyzac/TournamentMaker.git
   cd TournamentMaker/TournoiApp 
   ```

2. **Installer les dépendances :**
   ```bash
   pip install django certifi geopy 
   ```

3. **Préparer la base de données :**
   ```bash
   python manage.py makemigrations
   ```
   > Crée les fichiers de mise à jour pour la base de données.

   ```bash
   python manage.py migrate
   ```
   > Applique les changements dans la base de données.

4. **Lancer le serveur de développement :**
   ```bash
   python manage.py runserver
   ```

5. **Ouvrir l’application dans le navigateur :**
   [http://127.0.0.1:8000/TournamentMaker/](http://127.0.0.1:8000/TournamentMaker/)

---

## 🎯 Utilisateurs ciblés

Notre plateforme s’adresse à **deux types de profils** :

1. 👤 **Organisateur**
   - Crée, gère et planifie un tournoi sportif
   - Accède à une interface d’administration complète (équipes, matchs, scores, classement…)

2. 🧍 **Joueur ou spectateur**
   - Consulte les informations du tournoi (planning, résultats, classement)
   - Suit l’évolution de son équipe ou des autres en temps réel


### 🔐 Accès à l’interface d’administration

Créer un superutilisateur :
```bash
python manage.py createsuperuser
```
Puis accéder à l’interface :  
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧑‍💻 Developer Guide

### 📁 Structure du projet

```plaintext
TOURNAMENTMAKER/
│
├── manage.py
├── db.sqlite3
├── README.md
├── .gitignore
│
├── TournioApp/                     # Application Django principale
│   ├── __init__.py
│   ├── admin.py                    # Configure l’administration
│   ├── apps.py                     # Configuration de l'app
│   ├── context_processors.py       # Variables globales pour les templates
│   ├── models.py                   # Définition des modèles (tables)
│   ├── tests.py                    # Tests unitaires
│   ├── urls.py                     # Routes spécifiques à l'app
│   ├── views.py                    # Logique des pages
│   ├── migrations/                 # Historique des changements de la base
│   ├── management/                 # Commandes personnalisées (optionnel)
│   ├── services/                   # Code métier réutilisable
│   ├── static/                     # Fichiers CSS, JS, images
│   ├── templates/                  # Fichiers HTML
│   └── templatetags/               # Tags/filtres personnalisés
│
├── TournoiApp/                     # Dossier principal du projet Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Configuration globale du projet
│   ├── urls.py
│   └── wsgi.py
│
└── [autres fichiers éventuels...]
```

---

### ➕ Création d’une nouvelle app

```bash
python manage.py startapp nom_de_votre_app
```

> 🔁 N'oubliez pas d’ajouter l’app dans `INSTALLED_APPS` de `settings.py`.

---

### 🛠️ Ajouter des modèles et gérer les migrations

1. Écrire les modèles dans `models.py`
2. Générer les migrations :
    ```bash
    python manage.py makemigrations
    ```
3. Appliquer les migrations :
    ```bash
    python manage.py migrate
    ```

---

## 📂 Autres fichiers utiles

- `.gitignore` : fichiers/dossiers ignorés par Git
- `README.md` : ce fichier

---

## 📬 Contact

Pour toute question ou contribution, merci de contacter l’équipe de développement ou d’ouvrir un ticket sur le dépôt Git.
