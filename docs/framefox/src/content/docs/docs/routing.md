---
title: Système de routing
description: Guide complet du système de routage dans Framefox
---

# Système de routing

Le système de routing de Framefox vous permet de définir facilement comment votre application répond aux différentes requêtes HTTP. Basé sur FastAPI, il offre une grande flexibilité avec une syntaxe claire.

## Décorateur @Route

Le décorateur `@Route` est la façon principale de définir des routes dans Framefox :

```python
from framefox.core.routing.decorator.route import Route

@Route(path="/users", name="user.index", methods=["GET"])
async def index(self):
    return {"users": []}
```

### Paramètres du décorateur

- **path** : Le chemin URL de la route
- **name** : Nom unique pour identifier la route
- **methods** : Liste des méthodes HTTP acceptées

## Types de routes

### Routes statiques

```python
@Route("/", "home.index", methods=["GET"])
async def home(self):
    return self.render("home.html")

@Route("/about", "about.page", methods=["GET"])
async def about(self):
    return self.render("about.html")
```

### Routes avec paramètres

```python
# Paramètre simple
@Route("/users/{id}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    return {"user_id": id}

# Paramètres multiples
@Route("/users/{user_id}/posts/{post_id}", "user.post.show", methods=["GET"])
async def show_user_post(self, user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# Paramètre optionnel avec valeur par défaut
@Route("/posts/{category}", "post.by_category", methods=["GET"])
async def posts_by_category(self, category: str = "general"):
    return {"category": category}
```

### Routes avec expressions régulières

```python
# Contraintes sur les paramètres
@Route("/users/{id:int}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    # id est forcément un entier
    return {"user_id": id}

@Route("/posts/{slug:str}", "post.show", methods=["GET"])
async def show_post(self, slug: str):
    # slug est forcément une chaîne
    return {"post_slug": slug}
```

## Méthodes HTTP

### Méthodes courantes

```python
# GET - Récupérer des données
@Route("/users", "user.index", methods=["GET"])
async def get_users(self):
    return {"users": []}

# POST - Créer des données
@Route("/users", "user.create", methods=["POST"])
async def create_user(self, request: Request):
    data = await request.json()
    return {"created": True}

# PUT - Mettre à jour complètement
@Route("/users/{id}", "user.update", methods=["PUT"])
async def update_user(self, id: int, request: Request):
    return {"updated": True}

# PATCH - Mise à jour partielle
@Route("/users/{id}", "user.patch", methods=["PATCH"])
async def patch_user(self, id: int, request: Request):
    return {"patched": True}

# DELETE - Supprimer
@Route("/users/{id}", "user.delete", methods=["DELETE"])
async def delete_user(self, id: int):
    return {"deleted": True}
```

### Méthodes multiples

Une même méthode peut gérer plusieurs verbes HTTP :

```python
@Route("/contact", "contact.form", methods=["GET", "POST"])
async def contact(self, request: Request):
    if request.method == "GET":
        return self.render("contact/form.html")
    elif request.method == "POST":
        # Traiter le formulaire
        return self.redirect("contact.success")
```

## Nommage des routes

### Convention de nommage

Utilisez une convention cohérente pour nommer vos routes :

```python
# Format : ressource.action
@Route("/users", "user.index", methods=["GET"])          # Liste
@Route("/users/create", "user.create", methods=["GET"])  # Formulaire
@Route("/users", "user.store", methods=["POST"])         # Enregistrer
@Route("/users/{id}", "user.show", methods=["GET"])      # Afficher
@Route("/users/{id}/edit", "user.edit", methods=["GET"]) # Formulaire édition
@Route("/users/{id}", "user.update", methods=["PUT"])    # Mettre à jour
@Route("/users/{id}", "user.delete", methods=["DELETE"]) # Supprimer
```

### Groupes de routes

Pour les APIs ou modules :

```python
# API
@Route("/api/users", "api.user.index", methods=["GET"])
@Route("/api/users/{id}", "api.user.show", methods=["GET"])

# Admin
@Route("/admin/users", "admin.user.index", methods=["GET"])
@Route("/admin/users/{id}", "admin.user.show", methods=["GET"])
```

## Génération d'URLs

### Dans les contrôleurs

```python
# Redirection vers une route nommée
return self.redirect("user.show", id=123)

# Génération d'URL
url = self.url_for("user.edit", id=user.id)
```

### Dans les templates

```html
<!-- Lien simple -->
<a href="{{ url_for('user.index') }}">Tous les utilisateurs</a>

<!-- Lien avec paramètres -->
<a href="{{ url_for('user.show', id=user.id) }}">Voir {{ user.name }}</a>

<!-- Lien avec paramètres multiples -->
<a href="{{ url_for('user.post.show', user_id=user.id, post_id=post.id) }}">
    Voir le post
</a>
```

## Query Parameters

### Récupération des paramètres

```python
from fastapi import Request

@Route("/search", "search.index", methods=["GET"])
async def search(self, request: Request):
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", 1))
    
    return {
        "query": query,
        "page": page,
        "results": []
    }
```

### Avec Pydantic

```python
from pydantic import BaseModel

class SearchQuery(BaseModel):
    q: str = ""
    page: int = 1
    limit: int = 10

@Route("/search", "search.index", methods=["GET"])
async def search(self, query: SearchQuery):
    return {
        "query": query.q,
        "page": query.page,
        "results": []
    }
```

## Groupes et préfixes

### Organisation par modules

```python
# src/controllers/api/user_controller.py
class UserApiController(AbstractController):
    @Route("/api/v1/users", "api.v1.user.index", methods=["GET"])
    async def index(self):
        return {"users": []}
    
    @Route("/api/v1/users/{id}", "api.v1.user.show", methods=["GET"])
    async def show(self, id: int):
        return {"user": {}}
```

### Factorisation des préfixes

Pour éviter la répétition, vous pouvez utiliser des variables :

```python
class UserApiController(AbstractController):
    BASE_ROUTE = "/api/v1/users"
    
    @Route(f"{BASE_ROUTE}", "api.v1.user.index", methods=["GET"])
    async def index(self):
        return {"users": []}
    
    @Route(f"{BASE_ROUTE}/{{id}}", "api.v1.user.show", methods=["GET"])
    async def show(self, id: int):
        return {"user": {}}
```

## Routes conditionnelles

### Basées sur l'environnement

```python
from framefox.core.config.settings import Settings

class DebugController(AbstractController):
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @Route("/debug/info", "debug.info", methods=["GET"])
    async def debug_info(self):
        if self.settings.app_env != "dev":
            raise HTTPException(status_code=404)
        return {"debug": "info"}
```

## Routes de fallback

### Route catch-all

```python
@Route("/{path:path}", "fallback", methods=["GET"])
async def fallback(self, path: str):
    # Gère toutes les routes non définies
    return self.render("404.html", {"path": path}), 404
```

## Middleware de routes

### Protection par authentification

```python
from framefox.core.security.decorators import RequireAuth

@Route("/profile", "user.profile", methods=["GET"])
@RequireAuth
async def profile(self):
    return self.render("user/profile.html")
```

### Validation CSRF

```python
@Route("/users", "user.create", methods=["POST"])
async def create_user(self, request: Request):
    # CSRF automatiquement vérifié par le middleware
    return {"created": True}
```

## Debug et développement

### Lister toutes les routes

```bash
framefox debug router
```

Cette commande affiche :
- Le chemin de chaque route
- Le nom de la route
- Les méthodes HTTP acceptées
- Le contrôleur et la méthode associés

### Profiler web

En mode développement, accédez à `/_profiler` pour voir :
- Les routes appelées
- Les temps de réponse
- Les paramètres reçus

## Routes d'API REST

### Structure RESTful complète

```python
class ProductController(AbstractController):
    # GET /products - Liste tous les produits
    @Route("/products", "product.index", methods=["GET"])
    async def index(self):
        return {"products": []}
    
    # POST /products - Crée un nouveau produit
    @Route("/products", "product.store", methods=["POST"])
    async def store(self, request: Request):
        return {"created": True}
    
    # GET /products/{id} - Affiche un produit
    @Route("/products/{id}", "product.show", methods=["GET"])
    async def show(self, id: int):
        return {"product": {}}
    
    # PUT /products/{id} - Met à jour un produit
    @Route("/products/{id}", "product.update", methods=["PUT"])
    async def update(self, id: int, request: Request):
        return {"updated": True}
    
    # DELETE /products/{id} - Supprime un produit
    @Route("/products/{id}", "product.destroy", methods=["DELETE"])
    async def destroy(self, id: int):
        return {"deleted": True}
```

## Bonnes pratiques

### 1. Nommage cohérent

```python
# ✅ Bon
@Route("/users", "user.index", methods=["GET"])
@Route("/users/{id}", "user.show", methods=["GET"])

# ❌ Mauvais
@Route("/users", "list_users", methods=["GET"])
@Route("/users/{id}", "show_user_detail", methods=["GET"])
```

### 2. Groupement logique

```python
# ✅ Organisé par contrôleur
class UserController(AbstractController):
    pass

class PostController(AbstractController):
    pass
```

### 3. Validation des paramètres

```python
# ✅ Avec validation de type
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):  # FastAPI valide automatiquement
    pass
```

### 4. Gestion d'erreurs

```python
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    user = self.user_service.find(id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"user": user}
```

Le système de routing de Framefox offre une grande flexibilité tout en restant simple à utiliser. Il s'intègre parfaitement avec FastAPI pour vous donner accès à toutes ses fonctionnalités avancées.
