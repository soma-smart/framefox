---
title: Installation et configuration
description: Guide complet pour installer et configurer Framefox
---

# Installation et configuration

## Prérequis

Avant d'installer Framefox, assurez-vous d'avoir :

- **Python 3.8+** installé sur votre système
- **pip** (gestionnaire de paquets Python)
- Un éditeur de code (VS Code, PyCharm, etc.)

## Installation via pip

La méthode la plus simple pour installer Framefox :

```bash
pip install framefox
```

### Installation dans un environnement virtuel (recommandé)

```bash
# Créer un environnement virtuel
python -m venv framefox-env

# Activer l'environnement virtuel
# Sur Linux/macOS :
source framefox-env/bin/activate
# Sur Windows :
framefox-env\Scripts\activate

# Installer Framefox
pip install framefox
```

## Créer un nouveau projet

Une fois Framefox installé, créez votre premier projet :

```bash
# Créer le dossier du projet
mkdir mon-premier-projet
cd mon-premier-projet

# Initialiser le projet Framefox
framefox init
```

Cette commande créera automatiquement la structure de base :

```
mon-premier-projet/
├── src/
│   ├── controllers/
│   ├── entities/
│   ├── forms/
│   ├── repository/
│   └── templates/
├── public/
│   ├── css/
│   ├── js/
│   └── images/
├── config/
│   ├── services.yaml
│   ├── routing.yaml
│   └── security.yaml
├── main.py
└── requirements.txt
```

## Configuration de base

### Configuration de l'application

Le fichier `config/app.yaml` contient les paramètres principaux :

```yaml
app:
  name: "Mon Application Framefox"
  version: "1.0.0"
  environment: "dev"  # dev, prod, test
  debug: true
  secret_key: "votre-clé-secrète-très-longue"

database:
  default:
    driver: "sqlite"
    path: "database.db"
    # Ou pour MySQL/PostgreSQL :
    # host: "localhost"
    # port: 3306
    # username: "user"
    # password: "password"
    # database: "ma_db"

template:
  directory: "src/templates"
  cache: false  # true en production
```

### Configuration des services

Le fichier `config/services.yaml` définit l'injection de dépendances :

```yaml
services:
  # Configuration automatique pour les contrôleurs
  _defaults:
    autowire: true
    autoconfigure: true

  # Services personnalisés
  App\Service\EmailService:
    arguments:
      $smtpHost: '%env(SMTP_HOST)%'
      $smtpPort: '%env(SMTP_PORT)%'
```

## Vérification de l'installation

Démarrez le serveur de développement :

```bash
framefox serve
```

Visitez `http://localhost:8000` dans votre navigateur. Vous devriez voir la page d'accueil par défaut de Framefox !

## Configuration avancée

### Variables d'environnement

Créez un fichier `.env` à la racine de votre projet :

```env
APP_ENV=dev
APP_DEBUG=true
APP_SECRET=votre-clé-secrète-super-longue

DATABASE_URL=sqlite:///database.db
# DATABASE_URL=mysql://user:password@localhost:3306/database
# DATABASE_URL=postgresql://user:password@localhost:5432/database

SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
```

### Configuration de la base de données

Pour utiliser MySQL ou PostgreSQL, installez les drivers nécessaires :

```bash
# Pour MySQL
pip install pymysql

# Pour PostgreSQL  
pip install psycopg2-binary
```

Puis configurez la connexion dans `config/app.yaml` :

```yaml
database:
  default:
    driver: "mysql"  # ou "postgresql"
    host: "localhost"
    port: 3306
    username: "myuser"
    password: "mypassword"
    database: "mydatabase"
    charset: "utf8mb4"
```

## Commandes utiles

Une fois votre projet configuré, voici les commandes principales :

```bash
# Démarrer le serveur de développement
framefox serve

# Créer un contrôleur
framefox create controller

# Créer une entité
framefox create entity

# Gérer la base de données
framefox database create
framefox database migrate

# Lister les routes
framefox debug router

# Tests
framefox test
```

## Prochaines étapes

- [Créer votre premier contrôleur](/docs/controllers)
- [Configurer la base de données](/docs/database)
- [Système de routing](/docs/routing)
