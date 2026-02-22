# 💰 Budget Pro - Gestion de Finances Personnelles

**Budget Pro** est une application web moderne et sécurisée conçue pour vous aider à suivre vos revenus, vos dépenses et à atteindre vos objectifs d'épargne. Avec une interface "Glassmorphism" élégante et des visualisations de données dynamiques, gérer son argent n'a jamais été aussi simple.

## 🚀 Fonctionnalités

- **Authentification Sécurisée** : Inscription et connexion avec hachage de mot de passe et jetons JWT.
- **Tableau de Bord Dynamique** : Vue d'ensemble en temps réel de votre solde, vos revenus et vos dépenses.
- **Gestion des Transactions** : Ajoutez, visualisez et supprimez vos transactions facilement.
- **Objectifs d'Épargne** : Définissez des objectifs et suivez votre progression avec des barres de progression animées.
- **Analyses Visuelles** : Diagrammes circulaires pour la répartition des dépenses et graphiques linéaires pour l'évolution du solde.
- **Filtres Avancés** : Recherchez et filtrez vos transactions par catégorie, type ou période.
- **Export CSV** : Exportez vos données pour une analyse approfondie dans Excel ou Google Sheets.
- **Alertes de Budget** : Notifications visuelles lorsque vos dépenses dépassent un certain seuil.

## 🛠️ Stack Technique

- **Backend** : Python 3, Flask, SQLAlchemy, Flask-JWT-Extended.
- **Frontend** : React, TypeScript, Vite, Framer Motion (animations), Recharts (graphiques), Lucide React (icônes).
- **Base de Données** : SQLite.

## 📦 Installation et Lancement

### Prérequis
- Python 3.x
- Node.js (npm)

### 1. Configuration du Backend
```bash
# Entrer dans le dossier racine
# Créer et activer l'environnement virtuel (si pas déjà fait)
python -m venv venv
.\venv\Scripts\activate

# Installer les dépendances (Flask, SQLAlchemy, etc.)
pip install flask flask-sqlalchemy flask-cors flask-jwt-extended passlib

# Lancer le serveur
python app.py
```
*Le serveur tournera sur `http://127.0.0.1:5000`.*

### 2. Configuration du Frontend
```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer l'application
npm run dev
```
*L'application sera accessible sur `http://localhost:5173`.*

## 📸 Aperçu
L'interface utilise un design **Glassmorphism** avec un mode sombre optimisé pour une expérience utilisateur premium.

---
Projet développé avec ❤️ par Nazir et Nana.
