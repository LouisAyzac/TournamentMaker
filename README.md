
# 🏆 TournamentMaker

**TournamentMaker** est une application web développée avec **Django**. Elle permet de **créer**, **gérer** et **suivre facilement des tournois sportifs**, quels que soient le sport (football, basketball, handball, rugby, etc.).

Ce projet a été réalisé dans un cadre pédagogique afin de renforcer nos compétences en développement web, gestion de version avec Git, et travail d’équipe.

---

## 🎯 Utilisateurs ciblés

Notre plateforme s’adresse à **deux types de profils** :

1. 👤 **Organisateurs**
   - Créent et planifient leurs propres tournois
   - Ajoutent des équipes et joueurs
   - Gèrent les matchs, scores, et classements
   - Accèdent à une interface d'administration dédiée

2. 🧍 **Joueurs et spectateurs**
   - Consultent les informations du tournoi (planning, résultats, scores)
   - Suivent l’évolution des équipes en temps réel
   - Peuvent visualiser le classement général et les matchs à venir

---

## ✨ Fonctionnalités principales

- Création de tournois personnalisés
- Ajout et gestion d’équipes ou de joueurs
- Génération automatique des rencontres
- Mise à jour des scores en direct
- Visualisation des classements et calendriers
- Interface administrateur sécurisée

---

## 🛠️ Technologies utilisées

- [Python](https://www.python.org) – Langage principal
- [Django](https://www.djangoproject.com) – Framework web back-end
- [HTML](https://developer.mozilla.org/fr/docs/Web/HTML) – Structure des pages
- [CSS](https://developer.mozilla.org/fr/docs/Web/CSS) – Mise en forme
- [JavaScript](https://developer.mozilla.org/fr/docs/Web/JavaScript) – Interactivité (optionnel/à étendre)

> **Branche principale de développement** : `dev`

---

## 🧑‍💻 Installation & Lancement

### 🔧 Prérequis

- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)
- Git

### 🚀 Étapes d’installation

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

### 🔐 Interface d’administration Django

1. Créer un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```

2. Se connecter à l'admin :
   [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---


---

### 💻 Détail des commandes utilisées

Voici une explication détaillée de chaque commande utilisée lors de l’installation et du lancement de l’application :

#### 🔹 Clonage du dépôt
```bash
git clone https://github.com/LouisAyzac/TournamentMaker.git
```
> Clone le projet depuis GitHub dans un dossier local nommé `TournamentMaker`.

```bash
cd TournamentMaker/TournoiApp
```
> Se déplace dans le dossier contenant le cœur de l’application Django.

#### 🔹 Installation des dépendances
```bash
pip install -r requirements.txt
```
> Installe toutes les bibliothèques Python listées dans le fichier `requirements.txt` (ex: Django, certifi, etc.). Cela garantit que le projet dispose de tout le nécessaire pour fonctionner.

#### 🔹 Migrations de la base de données
```bash
python manage.py makemigrations
```
> Génère les fichiers de migration à partir des modèles définis dans `models.py`. Ces fichiers décrivent les changements à apporter à la base de données (tables, champs, relations...).

```bash
python manage.py migrate
```
> Applique les migrations à la base de données SQLite. Cela crée les tables et les structures nécessaires pour faire fonctionner l’application.

#### 🔹 Lancement du serveur de développement
```bash
python manage.py runserver
```
> Lance le serveur web intégré de Django, accessible à l’adresse [http://127.0.0.1:8000](http://127.0.0.1:8000). Idéal pour tester localement.

#### 🔹 Création d’un superutilisateur
```bash
python manage.py createsuperuser
```
> Lance une procédure pour créer un compte administrateur. Ce compte permet de se connecter à l’interface d’administration Django à [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

---

Ces commandes sont toutes exécutées via la console ou le terminal. Elles sont essentielles pour faire fonctionner tout projet Django correctement.
## 📁 Architecture du projet

```plaintext
TournamentMaker/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
│
├── TournioApp/                    # Application principale
│   ├── admin.py                   # Configuration de l'interface d'admin
│   ├── models.py                  # Définition des modèles (équipes, tournois, matchs...)
│   ├── views.py                   # Logique des pages
│   ├── urls.py                    # Routage de l'app
│   ├── templates/                 # Fichiers HTML
│   ├── static/                    # Fichiers CSS/JS/images
│   ├── migrations/                # Historique des modifications de BDD
│   └── ...
│
├── TournoiApp/                    # Dossier de configuration globale
│   ├── settings.py                # Paramètres du projet Django
│   ├── urls.py                    # Routes principales
│   └── ...
```

---

## 🧰 Bonnes pratiques & conseils

- Utilisez des **branches** pour développer de nouvelles fonctionnalités
- Faites des **commits réguliers** avec des messages clairs
- Testez localement avant de fusionner vos PR

---

## 👥 Équipe projet

- **Ange Gagnard** – Dev Back-end / Visualisation
- **Pablo Minelian** – UX / Interface utilisateur
- **Florian Garcia--Salon** – Intégration front
- **Antoine Huang** – Gestion de projet
- **Louis Ayzac** – Lead Dev / GitHub
- **Rémy Abdoul Mazidou** – Déploiement & outils Git

---

## ✅ Améliorations futures

- Ajout d’un système d’authentification utilisateurs (joueurs / visiteurs)
- Interface responsive pour mobile
- Visualisation graphique du bracket / classement
- Notifications en temps réel (WebSocket ou polling)
- Export des données (PDF, CSV)

---

## 📜 Licence

Ce projet est à but éducatif. Libre de réutilisation et modification dans un cadre non commercial.
