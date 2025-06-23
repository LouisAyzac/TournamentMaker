# TournamentMaker

## Membres du projet 

- Ange Gagnard https://onlywei.github.io/explain-git-with-d3/
- Pablo Minelian https://ohmygit.org
- Florian Garcia--Salon "https://openclassrooms.com/fr/courses/7162856-gerez-du-code-avec-git-et-github"
- Antoine Huang (https://eagain.net/articles/git-for-computer-scientists/)
- Louis Ayzac https://youtube.com/watch?v=1ffBJ4sVUb4&t=125s
- Remy Adboul Mazidou https://agripongit.vincenttunru.com/

## Technologies 

- [Python](https://docs.python.org)
- [Django](http://django.org)

BRANCH DEV 

# TournamentMaker

TournamentMaker est une application web Django permettant de créer, gérer et suivre des tournois.

---

## 🧑‍💻 User Guide

### Prérequis

- Python 3.8 ou supérieur
- pip (installé avec Python)
- (optionnel) Environnement virtuel : `python -m venv env`

### Installation

1. **Cloner le dépôt :**
   ```bash
   git clone <lien-vers-le-repo>
   cd TournamentMaker/TournoiApp
   ```

2. **Créer un environnement virtuel (optionnel mais recommandé) :**
   ```bash
   python -m venv env
   source env/bin/activate  # Sous Windows : env\Scripts\activate
   ```

3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

4. **Appliquer les migrations :**
   ```bash
   python manage.py migrate
   ```

5. **Lancer le serveur :**
   ```bash
   python manage.py runserver
   ```

6. **Accéder à l’application :**
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