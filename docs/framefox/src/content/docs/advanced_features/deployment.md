---
title: Déploiement
description: Déployez votre application Framefox en production
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Déploiement de votre application Framefox

Ce guide vous montre comment déployer votre application Framefox en production, en utilisant différentes méthodes et plateformes.

## Préparation au déploiement

Avant de déployer votre application, vous devez vous assurer qu'elle est prête pour la production :

### Configuration des environnements

Framefox utilise des variables d'environnement pour distinguer les environnements de développement, de test et de production. Configurez votre application en fonction de l'environnement dans `config/application.yaml` :

<CodeBlock
  code={`application:
  env: "%env(APP_ENV)%"  # Peut être "dev", "test", ou "prod"
  debug: "%env(APP_DEBUG)%"
  
  # Configuration spécifique aux environnements
  environments:
    dev:
      debug: true
      profiler: true
      
    test:
      debug: true
      profiler: false
      
    prod:
      debug: false
      profiler: false
      error_handler: "src.error.production_error_handler.ProductionErrorHandler"`}
  lang="yaml"
  filename="config/application.yaml"
/>

### Vérification de l'application

Avant le déploiement, exécutez les commandes suivantes pour vous assurer que votre application est prête :

<CodeBlock
  code={`# Vérifier la configuration de l'application
framefox debug:config

# Exécuter les tests
framefox test

# Vérifier les problèmes de sécurité
framefox security:audit

# Optimiser l'application pour la production
framefox cache:clear
framefox cache:warmup`}
  lang="bash"
/>

## Méthodes de déploiement

### 1. Déploiement traditionnel avec WSGI/ASGI

Framefox utilise ASGI pour une performance optimale. Vous pouvez utiliser Uvicorn, Hypercorn ou Daphne comme serveurs ASGI.

#### Configuration avec Uvicorn et Gunicorn

Pour la production, il est recommandé d'utiliser Gunicorn comme gestionnaire de processus avec Uvicorn comme worker :

<CodeBlock
  code={`# Installer les dépendances
pip install gunicorn uvicorn

# Créer un fichier gunicorn.conf.py
import multiprocessing

# Configuration Gunicorn
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120

# Configuration du logging
accesslog = "/var/log/framefox/access.log"
errorlog = "/var/log/framefox/error.log"
loglevel = "info"

# Configuration avancée
proc_name = "framefox"
keepalive = 65
backlog = 2048`}
  lang="python"
  filename="gunicorn.conf.py"
/>

#### Script de démarrage

<CodeBlock
  code={`#!/bin/bash
# start.sh

# Définir les variables d'environnement
export APP_ENV=prod
export APP_DEBUG=0

# Exécuter les migrations si nécessaire
python -m framefox migration:run

# Démarrer l'application avec Gunicorn
gunicorn -c gunicorn.conf.py main:app`}
  lang="bash"
  filename="start.sh"
/>

N'oubliez pas de rendre le script exécutable :

<CodeBlock
  code={`chmod +x start.sh`}
  lang="bash"
/>

### 2. Déploiement avec Docker

Docker est une excellente option pour déployer des applications Framefox de manière cohérente et isolée.

#### Dockerfile

<CodeBlock
  code={`# Dockerfile
FROM python:3.12-slim

# Définir les variables d'environnement
ENV APP_ENV=prod
ENV APP_DEBUG=0
ENV PYTHONUNBUFFERED=1

# Créer un utilisateur non root
RUN adduser --disabled-password --gecos '' framefox

# Créer le répertoire de l'application
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Définir les permissions
RUN chown -R framefox:framefox /app
USER framefox

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]`}
  lang="dockerfile"
  filename="Dockerfile"
/>

#### docker-compose.yml

<CodeBlock
  code={`# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    restart: always
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - APP_ENV=prod
      - APP_DEBUG=0
      - DATABASE_URL=postgresql://framefox:password@db:5432/framefox
    volumes:
      - ./logs:/app/var/log
    command: >
      bash -c "python -m framefox migration:run &&
               gunicorn -c gunicorn.conf.py main:app"
  
  db:
    image: postgres:16
    restart: always
    environment:
      - POSTGRES_USER=framefox
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=framefox
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - ./public:/app/public
    depends_on:
      - app

volumes:
  postgres_data:`}
  lang="yaml"
  filename="docker-compose.yml"
/>

#### Configuration Nginx

<CodeBlock
  code={`# nginx/conf.d/app.conf
server {
    listen 80;
    server_name example.com www.example.com;
    
    # Redirection vers HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name example.com www.example.com;
    
    # Certificats SSL
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # Configuration SSL optimisée
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    # Fichiers statiques
    location /static/ {
        alias /app/public/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Proxy vers l'application
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering on;
        proxy_buffer_size 16k;
        proxy_busy_buffers_size 24k;
        proxy_buffers 64 4k;
    }
}`}
  lang="nginx"
  filename="nginx/conf.d/app.conf"
/>

### 3. Déploiement sur des plateformes cloud

#### Heroku

<CodeBlock
  code={`# Procfile
web: gunicorn -k uvicorn.workers.UvicornWorker main:app

# runtime.txt
python-3.12.0`}
  lang="text"
  filename="Procfile"
/>

Commandes de déploiement :

<CodeBlock
  code={`# Créer une application Heroku
heroku create mon-app-framefox

# Ajouter une base de données PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configurer les variables d'environnement
heroku config:set APP_ENV=prod
heroku config:set APP_DEBUG=0

# Déployer l'application
git push heroku main

# Exécuter les migrations
heroku run python -m framefox migration:run`}
  lang="bash"
/>

#### AWS Elastic Beanstalk

Créez un fichier de configuration pour Elastic Beanstalk :

<CodeBlock
  code={`# .ebextensions/01_framefox.config
option_settings:
  aws:elasticbeanstalk:application:environment:
    APP_ENV: prod
    APP_DEBUG: 0
    
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
    
container_commands:
  01_migrations:
    command: "python -m framefox migration:run"
    leader_only: true
  
  02_collectstatic:
    command: "python -m framefox assets:install"
    
  03_create_superuser:
    command: "python -m framefox security:create-admin"
    leader_only: true`}
  lang="yaml"
  filename=".ebextensions/01_framefox.config"
/>

Déployez avec la commande :

<CodeBlock
  code={`# Initialiser l'application Elastic Beanstalk
eb init -p python-3.12 mon-app-framefox

# Créer un environnement et déployer
eb create production-environment`}
  lang="bash"
/>

## Bonnes pratiques de déploiement

### 1. Surveillance et journalisation

Framefox peut être configuré pour intégrer des outils de surveillance comme Sentry ou ELK Stack.

<CodeBlock
  code={`# config/services.yaml
services:
  logger:
    class: src.service.logging.sentry_logger.SentryLogger
    arguments:
      - "%env(SENTRY_DSN)%"
      - "%app.env%"`}
  lang="yaml"
  filename="config/services.yaml"
/>

### 2. Mise en cache

Pour améliorer les performances en production, configurez le cache :

<CodeBlock
  code={`# config/cache.yaml
cache:
  default: redis
  
  stores:
    redis:
      driver: redis
      host: "%env(REDIS_HOST)%"
      port: "%env(REDIS_PORT)%"
      password: "%env(REDIS_PASSWORD)%"
      
  ttl: 3600  # Durée par défaut en secondes`}
  lang="yaml"
  filename="config/cache.yaml"
/>

### 3. Serveur de tâches asynchrones

Pour les tâches longues, utilisez un serveur de tâches comme Dramatiq ou Celery :

<CodeBlock
  code={`# config/tasks.yaml
task_server:
  driver: dramatiq
  broker: redis
  
  redis:
    host: "%env(REDIS_HOST)%"
    port: "%env(REDIS_PORT)%"
    password: "%env(REDIS_PASSWORD)%"
    
  workers: 4`}
  lang="yaml"
  filename="config/tasks.yaml"
/>

### 4. Sauvegarde et restauration

Mettez en place un système de sauvegarde régulière de votre base de données :

<CodeBlock
  code={`#!/bin/bash
# scripts/backup.sh

# Variables
DB_USER="framefox"
DB_PASSWORD="password"
DB_NAME="framefox"
BACKUP_DIR="/var/backups/framefox"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

# Créer le répertoire de sauvegarde si nécessaire
mkdir -p $BACKUP_DIR

# Créer la sauvegarde
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Rotation des sauvegardes (conserver les 7 dernières)
ls -t $BACKUP_DIR/backup_*.sql.gz | tail -n +8 | xargs rm -f

# Notification
echo "Sauvegarde créée: $BACKUP_FILE"`}
  lang="bash"
  filename="scripts/backup.sh"
/>

## Liste de contrôle pour le déploiement

Avant de déployer votre application Framefox en production, vérifiez les points suivants :

1. **Environnement de production configuré** (`APP_ENV=prod`)
2. **Débogage désactivé** (`APP_DEBUG=0`)
3. **Variables sensibles configurées en tant que variables d'environnement**
4. **Base de données configurée correctement pour la production**
5. **Migrations exécutées**
6. **Certificats SSL installés (pour HTTPS)**
7. **Système de journalisation configuré**
8. **Surveillance en place**
9. **Stratégie de sauvegarde implémentée**
10. **Tests exécutés avec succès**
11. **Mise en cache configurée**
12. **Performances optimisées**
13. **Sécurité auditée**

## Stratégies de déploiement

### Déploiement continu (CI/CD)

Exemple de configuration GitHub Actions pour un déploiement automatique :

<CodeBlock
  code={`# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m framefox test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "mon-app-framefox"
          heroku_email: ${{secrets.HEROKU_EMAIL}}
      - name: Run migrations
        run: |
          heroku run python -m framefox migration:run -a mon-app-framefox`}
  lang="yaml"
  filename=".github/workflows/deploy.yml"
/>

### Déploiement bleu-vert

Cette stratégie consiste à maintenir deux environnements identiques (bleu et vert) et à basculer entre eux :

<CodeBlock
  code={`#!/bin/bash
# scripts/blue-green-deploy.sh

# Variables
APP_NAME="mon-app-framefox"
BLUE_APP="${APP_NAME}-blue"
GREEN_APP="${APP_NAME}-green"
ROUTER_APP="${APP_NAME}-router"

# Déterminer l'environnement actif
CURRENT_APP=$(heroku config:get ACTIVE_APP -a $ROUTER_APP)

if [ "$CURRENT_APP" == "$BLUE_APP" ]; then
  TARGET_APP=$GREEN_APP
else
  TARGET_APP=$BLUE_APP
fi

echo "Déploiement vers $TARGET_APP..."

# Déployer vers l'environnement cible
git push https://git.heroku.com/$TARGET_APP.git main

# Exécuter les migrations
heroku run python -m framefox migration:run -a $TARGET_APP

# Vérifier que l'application fonctionne
HEALTH_CHECK=$(curl -s https://$TARGET_APP.herokuapp.com/health-check)

if [ "$HEALTH_CHECK" == '{"status":"ok"}' ]; then
  echo "Application en bon état, basculement du trafic..."
  
  # Basculer le trafic vers le nouvel environnement
  heroku config:set ACTIVE_APP=$TARGET_APP -a $ROUTER_APP
  
  echo "Déploiement terminé avec succès!"
else
  echo "Échec de la vérification de santé, abandon du déploiement."
  exit 1
fi`}
  lang="bash"
  filename="scripts/blue-green-deploy.sh"
/>

## Après le déploiement

Une fois votre application déployée, n'oubliez pas de :

1. **Surveiller les performances** : Utilisez des outils comme New Relic ou Datadog
2. **Vérifier les journaux** : Recherchez les erreurs ou les anomalies
3. **Tester l'application** : Assurez-vous que toutes les fonctionnalités fonctionnent
4. **Configurer des alertes** : Pour être informé des problèmes
5. **Documenter le processus** : Pour faciliter les déploiements futurs

Avec ces conseils, votre application Framefox sera correctement déployée et prête à être utilisée en production.
