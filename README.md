# 🏆 TournamentMaker

**TournamentMaker** est une application web développée avec **Django**. Elle permet de **créer**, **gérer** et **suivre facilement des tournois**, qu'ils soient sportifs, e-sport ou autres. Ce projet a été réalisé dans un cadre pédagogique afin de renforcer nos compétences en développement web, en gestion de version avec Git, et en travail d’équipe.

---

## 👥 Membres du projet

- **Ange Gagnard** – [Visualisation Git avec D3.js](https://onlywei.github.io/explain-git-with-d3/)
- **Pablo Minelian** – [Jeu pédagogique Git](https://ohmygit.org)
- **Florian Garcia--Salon** – [Cours OpenClassrooms : Git & GitHub](https://openclassrooms.com/fr/courses/7162856-gerez-du-code-avec-git-et-github)
- **Antoine Huang** – [Git for Computer Scientists](https://eagain.net/articles/git-for-computer-scientists/)
- **Louis Ayzac** – [Conférence Git (YouTube)](https://youtube.com/watch?v=1ffBJ4sVUb4&t=125s)
- **Rémy Adboul Mazidou** – [AgriponGit – Visualiseur Git](https://agripongit.vincenttunru.com/)

---

## ⚙️ Technologies utilisées

- [Python](https://docs.python.org) – Langage de programmation
- [Django](https://www.djangoproject.com) – Framework web back-end
- [HTML](https://developer.mozilla.org/fr/docs/Web/HTML) – Structure des pages
- [CSS](https://developer.mozilla.org/fr/docs/Web/CSS) – Mise en forme et design

> **Branche principale de développement** : `dev`

---

## 🚀 Fonctionnalités principales

- Création de tournois personnalisés
- Ajout de joueurs ou d’équipes
- Génération automatique des matchs
- Suivi des scores et des résultats
- Tableau d’administration sécurisé

---

## 🧑‍💻 Guide d'installation (User Guide)

### ✅ Prérequis

- [Python 3.8 ou supérieur] (https://www.python.org/downloads/)
- pip (installé avec Python)
- (optionnel) Environnement virtuel Python

### 📥 Installation

# 🛠️ Installation de Django

## Prérequis

- **Python 3.8** ou plus récent  
- **pip** (installé avec Python)  
- _(optionnel)_ **virtualenv** ou **venv** pour isoler l’environnement

---

## Étapes d’installation

### 1. Installer Python

Vérifie que Python est installé :

```bash
python --version
```

Si ce n’est pas le cas, télécharge-le ici : <https://www.python.org/downloads/>

---

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv env
```

Active-le :

- **Linux / macOS**

  ```bash
  source env/bin/activate
  ```

- **Windows**

  ```bash
  env\Scripts\activate
  ```

---

### 3. Mettre à jour `pip`

```bash
pip install --upgrade pip
```

---

### 4. Installer Django

```bash
pip install django
```

Vérifie l’installation :

```bash
django-admin --version
```

---

### 5. Créer un projet Django

```bash
django-admin startproject monprojet
cd monprojet
python manage.py runserver
```

Puis ouvre ton navigateur et visite : <http://127.0.0.1:8000>

---

_Félicitations ! Django est maintenant installé et opérationnel._

1. **Cloner le dépôt dans un dossier vide :**
   ```bash
   git clone https://github.com/LouisAyzac/TournamentMaker.git
   cd TournamentMaker/TournoiApp

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Appliquer les migrations :**
   ```bash
   python manage.py migrate
   ```

4. **Lancer le serveur :**
   ```bash
   python manage.py runserver
   ```

5. **Accéder à l’application :**
   Ouvrez votre navigateur à l’adresse : [http://localhost:8000](http://localhost:8000)

---

## 🛠 Developer Guide

### Structure du projet

```
TournamentMaker/
└── TournoiApp/
    ├── manage.py
    └── TournoiApp/
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
        └── asgi.py
```

### Création d’une nouvelle app

```bash
python manage.py startapp nom_de_votre_app
```

Pensez à ajouter l’app dans `INSTALLED_APPS` de `settings.py`.

### Ajout de modèles et migrations

1. Définir les modèles dans `models.py`
2. Exécuter :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Interface d’administration

Créer un superutilisateur :
```bash
python manage.py createsuperuser
```
Puis accéder à : [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 📂 Autres fichiers utiles

- `.gitignore` : liste les fichiers/dossiers exclus du contrôle de version
- `README.md` : ce fichier

---

## 📬 Contact

Pour toute question ou contribution, merci de contacter l’équipe de développement ou d’ouvrir un ticket sur le dépôt Git.
