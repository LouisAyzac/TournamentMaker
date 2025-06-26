# 🏆 TournamentMaker

## 🧑‍💻 User Guide


---

### 🔐 Gestion des organisateurs et accès sécurisé

Lors de la **création d’un tournoi**, un **email** est demandé : il s’agit de l’adresse email de l’organisateur du tournoi.

Voici comment fonctionne l’accès sécurisé :

1. 📩 **Envoi automatique d’un email** :
   - Un email est envoyé à l’organisateur contenant un **lien pour définir son mot de passe**.
   - Ce mot de passe est strictement personnel et confidentiel.

2. 🔐 **Utilisation du compte organisateur** :
   - Ce compte permet à l’organisateur de :
     - 🔄 **Mettre à jour les scores** de toutes les équipes de son tournoi
     - 🏆 **Créer les phases finales** (playoffs, demi-finales, etc.)
   - À chaque action sensible (comme changer un score ou accéder aux phases finales), le **login et mot de passe** de l’organisateur sont demandés.

Cette fonctionnalité garantit que **seuls les organisateurs autorisés** peuvent modifier les éléments critiques d’un tournoi.


---

### 📧 Gestion des capitaines d’équipes

Lors de l’**inscription d’une équipe** à un tournoi, une adresse email est demandée au **capitaine** de l’équipe.

Voici comment cela fonctionne :

1. 📩 **Envoi automatique d’un email au capitaine** :
   - Un lien de création de mot de passe est envoyé à l’adresse fournie.
   - Ce mot de passe permet au capitaine d’accéder à une interface sécurisée dédiée.

2. 🔒 **Accès restreint pour les capitaines** :
   - Chaque capitaine peut uniquement :
     - 📝 **Mettre à jour les scores** de **son équipe uniquement**
   - Il n’a pas accès aux autres données du tournoi ni aux équipes adverses.

3. ✅ **Authentification obligatoire** :
   - Pour modifier le score de son équipe, le capitaine doit **s’authentifier** avec son email et mot de passe personnel.

Cela permet de responsabiliser les capitaines tout en assurant un contrôle précis et sécurisé des modifications autorisées.

---
---
### 🚀 Étapes d’installation
...
