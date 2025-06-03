---
title: Templates et vues
description: Guide complet du système de templates Jinja2 dans Framefox
---

# Templates et vues

Framefox utilise **Jinja2** comme moteur de templates, vous permettant de créer des vues dynamiques et réutilisables. Le système est intégré avec de nombreuses fonctionnalités spécifiques à Framefox.

## Structure des templates

### Organisation des fichiers

```
src/templates/
├── base.html              # Template de base
├── layouts/
│   ├── app.html          # Layout principal
│   └── admin.html        # Layout admin
├── components/
│   ├── navbar.html       # Composants réutilisables
│   └── footer.html
├── user/
│   ├── index.html        # Liste des utilisateurs
│   ├── show.html         # Détail utilisateur
│   └── form.html         # Formulaire utilisateur
└── errors/
    ├── 404.html          # Page d'erreur 404
    └── 500.html          # Page d'erreur 500
```

## Template de base

### base.html

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mon Application Framefox{% endblock %}</title>
    
    <!-- CSS -->
    <link href="{{ asset('css/bootstrap.min.css') }}" rel="stylesheet">
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
    {% block stylesheets %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home.index') }}">
                Mon App
            </a>
            
            <div class="navbar-nav ms-auto">
                {% if current_user %}
                    <a class="nav-link" href="{{ url_for('user.profile') }}">
                        {{ current_user.name }}
                    </a>
                    <a class="nav-link" href="{{ url_for('security.logout') }}">
                        Déconnexion
                    </a>
                {% else %}
                    <a class="nav-link" href="{{ url_for('security.login') }}">
                        Connexion
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        <!-- Messages flash -->
        {% for message in get_flash_messages() %}
            <div class="alert alert-{{ message.type }} alert-dismissible fade show">
                {{ message.content }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}

        {% block content %}{% endblock %}
    </main>

    <footer class="bg-dark text-white mt-5 py-4">
        <div class="container text-center">
            <p>&copy; 2024 Mon Application. Développé avec Framefox.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="{{ asset('js/bootstrap.bundle.min.js') }}"></script>
    {% block javascripts %}{% endblock %}
</body>
</html>
```

## Rendu depuis les contrôleurs

### Méthode render()

```python
from framefox.core.controller.abstract_controller import AbstractController

class UserController(AbstractController):
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
        
        return self.render("user/index.html", {
            "users": users,
            "page_title": "Liste des utilisateurs"
        })
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        user = {"id": id, "name": f"Utilisateur {id}"}
        
        return self.render("user/show.html", {
            "user": user
        })
```

### Avec layout personnalisé

```python
@Route("/admin/dashboard", "admin.dashboard", methods=["GET"])
async def dashboard(self):
    return self.render("admin/dashboard.html", {
        "stats": {"users": 150, "posts": 340}
    }, layout="layouts/admin.html")
```

## Templates de pages

### user/index.html

```html
{% extends "base.html" %}

{% block title %}{{ page_title }} - {{ super() }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1>{{ page_title }}</h1>
    <a href="{{ url_for('user.create') }}" class="btn btn-primary">
        Nouvel utilisateur
    </a>
</div>

{% if users %}
    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.id }}</td>
                    <td>{{ user.name }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                        <a href="{{ url_for('user.show', id=user.id) }}" 
                           class="btn btn-sm btn-outline-primary">
                            Voir
                        </a>
                        <a href="{{ url_for('user.edit', id=user.id) }}" 
                           class="btn btn-sm btn-outline-secondary">
                            Modifier
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
{% else %}
    <div class="alert alert-info">
        <p class="mb-0">Aucun utilisateur trouvé.</p>
    </div>
{% endif %}
{% endblock %}
```

### user/show.html

```html
{% extends "base.html" %}

{% block title %}{{ user.name }} - {{ super() }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h2>{{ user.name }}</h2>
            </div>
            <div class="card-body">
                <dl class="row">
                    <dt class="col-sm-3">ID</dt>
                    <dd class="col-sm-9">{{ user.id }}</dd>
                    
                    <dt class="col-sm-3">Nom</dt>
                    <dd class="col-sm-9">{{ user.name }}</dd>
                    
                    <dt class="col-sm-3">Email</dt>
                    <dd class="col-sm-9">{{ user.email }}</dd>
                    
                    <dt class="col-sm-3">Créé le</dt>
                    <dd class="col-sm-9">{{ user.created_at|date('d/m/Y H:i') }}</dd>
                </dl>
            </div>
            <div class="card-footer">
                <a href="{{ url_for('user.edit', id=user.id) }}" 
                   class="btn btn-primary">
                    Modifier
                </a>
                <a href="{{ url_for('user.index') }}" 
                   class="btn btn-secondary">
                    Retour à la liste
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Fonctions Framefox intégrées

### url_for()

Génère des URLs vers vos routes nommées :

```html
<!-- URL simple -->
<a href="{{ url_for('home.index') }}">Accueil</a>

<!-- URL avec paramètres -->
<a href="{{ url_for('user.show', id=123) }}">Utilisateur 123</a>

<!-- URL avec paramètres multiples -->
<a href="{{ url_for('user.post.show', user_id=1, post_id=5) }}">Post 5</a>
```

### asset()

Génère des liens vers vos assets statiques :

```html
<!-- CSS -->
<link href="{{ asset('css/app.css') }}" rel="stylesheet">

<!-- JavaScript -->
<script src="{{ asset('js/app.js') }}"></script>

<!-- Images -->
<img src="{{ asset('images/logo.png') }}" alt="Logo">
```

### csrf_token()

Protection CSRF automatique dans les formulaires :

```html
<form method="POST" action="{{ url_for('user.create') }}">
    {{ csrf_token() }}
    
    <div class="mb-3">
        <label for="name" class="form-label">Nom</label>
        <input type="text" class="form-control" id="name" name="name" required>
    </div>
    
    <button type="submit" class="btn btn-primary">Créer</button>
</form>
```

### current_user

Accès à l'utilisateur authentifié :

```html
{% if current_user %}
    <p>Bonjour {{ current_user.name }} !</p>
    <p>Votre email : {{ current_user.email }}</p>
{% else %}
    <p><a href="{{ url_for('security.login') }}">Se connecter</a></p>
{% endif %}
```

### get_flash_messages()

Affichage des messages flash :

```html
{% for message in get_flash_messages() %}
    <div class="alert alert-{{ message.type }} alert-dismissible fade show" role="alert">
        {{ message.content }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
{% endfor %}
```

### request

Accès à l'objet request actuel :

```html
<!-- URL actuelle -->
<p>URL actuelle : {{ request.url }}</p>

<!-- Paramètres GET -->
{% if request.query_params.get('search') %}
    <p>Recherche : {{ request.query_params.get('search') }}</p>
{% endif %}

<!-- Headers -->
<p>User-Agent : {{ request.headers.get('user-agent') }}</p>
```

## Formulaires

### Création de formulaires

```html
{% extends "base.html" %}

{% block title %}Créer un utilisateur - {{ super() }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Créer un utilisateur</h3>
            </div>
            <div class="card-body">
                <form method="POST">
                    {{ csrf_token() }}
                    
                    <div class="mb-3">
                        <label for="name" class="form-label">Nom complet</label>
                        <input type="text" 
                               class="form-control" 
                               id="name" 
                               name="name" 
                               value="{{ form.name.value if form.name.value else '' }}"
                               required>
                        {% if form.name.errors %}
                            <div class="text-danger">
                                {% for error in form.name.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" 
                               class="form-control" 
                               id="email" 
                               name="email" 
                               value="{{ form.email.value if form.email.value else '' }}"
                               required>
                        {% if form.email.errors %}
                            <div class="text-danger">
                                {% for error in form.email.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Mot de passe</label>
                        <input type="password" 
                               class="form-control" 
                               id="password" 
                               name="password" 
                               required>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">
                            Créer l'utilisateur
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Filtres Jinja2

### Filtres intégrés

```html
<!-- Formatage de dates -->
<p>Créé le : {{ user.created_at|date('d/m/Y à H:i') }}</p>

<!-- Formatage de texte -->
<h2>{{ post.title|upper }}</h2>
<p>{{ post.content|truncate(150) }}</p>

<!-- Formatage de nombres -->
<p>Prix : {{ product.price|round(2) }}€</p>

<!-- Échappement HTML -->
<div>{{ user_content|safe }}</div>  <!-- Sans échappement -->
<div>{{ user_content|escape }}</div>  <!-- Avec échappement -->
```

### Filtres personnalisés Framefox

```html
<!-- Diviser une chaîne -->
{% set tags = "php,python,javascript"|split(',') %}
{% for tag in tags %}
    <span class="badge bg-secondary">{{ tag }}</span>
{% endfor %}

<!-- Dernier élément d'une liste -->
<p>Dernier utilisateur : {{ users|last }}</p>

<!-- Valeurs min/max -->
<p>Prix minimum : {{ prices|min }}€</p>
<p>Prix maximum : {{ prices|max }}€</p>
```

## Macros

### Définition de macros

```html
<!-- macros/forms.html -->
{% macro input_field(name, label, type="text", value="", required=false) %}
<div class="mb-3">
    <label for="{{ name }}" class="form-label">
        {{ label }}
        {% if required %}<span class="text-danger">*</span>{% endif %}
    </label>
    <input type="{{ type }}" 
           class="form-control" 
           id="{{ name }}" 
           name="{{ name }}" 
           value="{{ value }}"
           {% if required %}required{% endif %}>
</div>
{% endmacro %}

{% macro submit_button(text="Valider", class="btn-primary") %}
<div class="d-grid">
    <button type="submit" class="btn {{ class }}">{{ text }}</button>
</div>
{% endmacro %}
```

### Utilisation des macros

```html
{% from "macros/forms.html" import input_field, submit_button %}

<form method="POST">
    {{ csrf_token() }}
    
    {{ input_field("name", "Nom complet", required=true) }}
    {{ input_field("email", "Email", type="email", required=true) }}
    {{ input_field("phone", "Téléphone") }}
    
    {{ submit_button("Créer l'utilisateur") }}
</form>
```

## Incluions et composants

### Inclusion de templates

```html
<!-- Navigation -->
{% include "components/navbar.html" %}

<!-- Contenu principal -->
<main>
    {% block content %}{% endblock %}
</main>

<!-- Pied de page -->
{% include "components/footer.html" %}
```

### Composants avec variables

```html
<!-- components/user-card.html -->
<div class="card mb-3">
    <div class="card-body">
        <h5 class="card-title">{{ user.name }}</h5>
        <p class="card-text">{{ user.email }}</p>
        {% if show_actions %}
        <div class="card-actions">
            <a href="{{ url_for('user.show', id=user.id) }}" class="btn btn-primary btn-sm">
                Voir
            </a>
        </div>
        {% endif %}
    </div>
</div>

<!-- Utilisation -->
{% for user in users %}
    {% include "components/user-card.html" with context %}
{% endfor %}
```

## Gestion des erreurs

### Page 404

```html
<!-- errors/404.html -->
{% extends "base.html" %}

{% block title %}Page non trouvée - {{ super() }}{% endblock %}

{% block content %}
<div class="text-center">
    <h1 class="display-1">404</h1>
    <p class="fs-3"><span class="text-danger">Oops!</span> Page non trouvée.</p>
    <p class="lead">La page que vous cherchez n'existe pas.</p>
    <a href="{{ url_for('home.index') }}" class="btn btn-primary">
        Retour à l'accueil
    </a>
</div>
{% endblock %}
```

### Page 500

```html
<!-- errors/500.html -->
{% extends "base.html" %}

{% block title %}Erreur interne - {{ super() }}{% endblock %}

{% block content %}
<div class="text-center">
    <h1 class="display-1">500</h1>
    <p class="fs-3"><span class="text-danger">Erreur!</span> Problème interne.</p>
    <p class="lead">Une erreur inattendue s'est produite.</p>
    {% if app.debug %}
        <div class="alert alert-danger text-start mt-4">
            <h4>Détails de l'erreur :</h4>
            <pre>{{ error_details }}</pre>
        </div>
    {% endif %}
    <a href="{{ url_for('home.index') }}" class="btn btn-primary">
        Retour à l'accueil
    </a>
</div>
{% endblock %}
```

## Configuration avancée

### Extension du moteur Jinja2

Dans votre configuration, vous pouvez étendre Jinja2 :

```python
# config/template_config.py
from jinja2 import Environment

def configure_jinja(env: Environment):
    # Fonctions globales personnalisées
    def format_currency(amount):
        return f"{amount:.2f}€"
    
    env.globals['format_currency'] = format_currency
    
    # Filtres personnalisés
    def slugify(text):
        import re
        return re.sub(r'[^\w\s-]', '', text).strip().lower()
    
    env.filters['slugify'] = slugify
```

### Variables globales

```python
# Dans votre contrôleur ou service
class TemplateService:
    def get_global_context(self):
        return {
            'app_name': 'Mon Application',
            'app_version': '1.0.0',
            'current_year': datetime.now().year
        }
```

## Bonnes pratiques

### 1. Organisation des fichiers

```
templates/
├── layouts/           # Layouts de base
├── pages/            # Pages complètes
├── components/       # Composants réutilisables
├── macros/           # Macros Jinja2
└── emails/           # Templates d'emails
```

### 2. Nommage cohérent

```html
<!-- ✅ Bon -->
{% extends "layouts/app.html" %}
{% include "components/user-card.html" %}

<!-- ❌ Mauvais -->
{% extends "main.html" %}
{% include "usercard.html" %}
```

### 3. Performance

```html
<!-- ✅ Mise en cache des inclusions -->
{% cache 3600 %}
{% include "components/heavy-component.html" %}
{% endcache %}

<!-- ✅ Lazy loading des assets -->
<img src="{{ asset('images/hero.jpg') }}" loading="lazy" alt="Hero">
```

### 4. Sécurité

```html
<!-- ✅ Échappement automatique activé par défaut -->
<p>{{ user_input }}</p>  <!-- Automatiquement échappé -->

<!-- ✅ Désactivation explicite si nécessaire -->
<div>{{ trusted_html|safe }}</div>

<!-- ✅ CSRF sur tous les formulaires -->
<form method="POST">
    {{ csrf_token() }}
    <!-- ... -->
</form>
```

Le système de templates de Framefox offre toute la puissance de Jinja2 avec des fonctionnalités supplémentaires spécifiquement conçues pour le développement web moderne.
