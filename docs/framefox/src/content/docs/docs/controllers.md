---
title: Contrôleurs
description: Guide complet sur les contrôleurs dans Framefox
---

# Contrôleurs

Les contrôleurs constituent le cœur de votre application Framefox. Ils gèrent les requêtes HTTP, orchestrent la logique métier et retournent les réponses appropriées.

## Créer un contrôleur

### Via le terminal interactif

```bash
framefox create controller
```

Le terminal vous demandera :
- Le nom du contrôleur
- Les routes à créer
- Le type de contrôleur (basique, CRUD, API)

### Manuellement

Créez un fichier dans `src/controllers/user_controller.py` :

```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from fastapi import Request

class UserController(AbstractController):
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        users = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        return self.render("user/index.html", {"users": users})
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        # Simuler la récupération d'un utilisateur
        user = {"id": id, "name": f"Utilisateur {id}"}
        return self.render("user/show.html", {"user": user})
```

## AbstractController

Tous vos contrôleurs doivent hériter de `AbstractController` qui fournit des méthodes utiles :

### Rendu de templates

```python
# Rendre un template avec des variables
return self.render("template.html", {"key": "value"})

# Rendre avec le layout par défaut
return self.render("page.html", {"data": data}, layout="base.html")
```

### Réponses JSON

```python
# Retourner du JSON
return self.json({"status": "success", "data": data})

# Réponse JSON avec code de statut
return self.json({"error": "Not found"}, status_code=404)
```

### Redirections

```python
# Redirection vers une route nommée
return self.redirect("user.index")

# Redirection avec paramètres
return self.redirect("user.show", id=123)

# Redirection vers une URL absolue
return self.redirect("https://example.com")
```

## Décorateur @Route

Le décorateur `@Route` définit les routes de vos méthodes :

```python
@Route(path, name, methods)
```

### Paramètres

- **path** : Le chemin URL (`/users`, `/users/{id}`)
- **name** : Nom unique de la route (`user.index`)
- **methods** : Liste des méthodes HTTP (`["GET", "POST"]`)

### Exemples

```python
# Route simple
@Route("/", "home.index", methods=["GET"])
async def index(self):
    return self.render("home.html")

# Route avec paramètre
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    return {"user_id": id}

# Route acceptant plusieurs méthodes
@Route("/contact", "contact.form", methods=["GET", "POST"])
async def contact(self, request: Request):
    if request.method == "POST":
        # Traiter le formulaire
        return self.redirect("contact.success")
    return self.render("contact/form.html")
```

## Paramètres de route

### Paramètres simples

```python
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    return {"user_id": id}

@Route("/posts/{slug}", "post.show", methods=["GET"])
async def show_post(self, slug: str):
    return {"post_slug": slug}
```

### Paramètres avec validation

```python
from pydantic import BaseModel

class UserQuery(BaseModel):
    page: int = 1
    limit: int = 10
    search: str = ""

@Route("/users", "user.search", methods=["GET"])
async def search(self, query: UserQuery):
    return {
        "page": query.page,
        "limit": query.limit,
        "search": query.search
    }
```

## Injection de dépendances

Framefox utilise l'injection de dépendances pour vos services :

```python
from src.service.user_service import UserService
from src.repository.user_repository import UserRepository

class UserController(AbstractController):
    def __init__(self, user_service: UserService, user_repo: UserRepository):
        self.user_service = user_service
        self.user_repo = user_repo
    
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        users = self.user_service.get_all_users()
        return self.render("user/index.html", {"users": users})
```

## Gestion des formulaires

### Création de formulaires

```python
from src.form.user_type import UserType

@Route("/users/create", "user.create", methods=["GET", "POST"])
async def create(self, request: Request):
    form = self.create_form(UserType)
    
    if request.method == "POST":
        await form.handle_request(request)
        if form.is_valid():
            user_data = form.get_data()
            # Créer l'utilisateur
            self.add_flash("success", "Utilisateur créé avec succès !")
            return self.redirect("user.index")
    
    return self.render("user/create.html", {"form": form})
```

### Validation des données

```python
from pydantic import BaseModel, EmailStr, validator

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    age: int
    
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 120:
            raise ValueError('Âge invalide')
        return v

@Route("/api/users", "api.user.create", methods=["POST"])
async def create_user_api(self, data: CreateUserRequest):
    # Les données sont automatiquement validées
    user = self.user_service.create_user(data)
    return self.json({"id": user.id, "name": user.name})
```

## Messages flash

Les messages flash permettent d'afficher des notifications temporaires :

```python
# Ajouter un message
self.add_flash("success", "Opération réussie !")
self.add_flash("error", "Une erreur s'est produite")
self.add_flash("info", "Information importante")

# Dans le template
{{ get_flash_messages() }}
```

## Contrôleurs CRUD

Framefox peut générer automatiquement des contrôleurs CRUD complets :

```bash
framefox create crud User
```

Cela générera :

```python
class UserController(AbstractController):
    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository
    
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        users = self.repository.find_all()
        return self.render("user/index.html", {"users": users})
    
    @Route("/users/create", "user.create", methods=["GET", "POST"])
    async def create(self, request: Request):
        # Logique de création
        pass
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        user = self.repository.find(id)
        return self.render("user/show.html", {"user": user})
    
    @Route("/users/{id}/edit", "user.edit", methods=["GET", "POST"])
    async def edit(self, id: int, request: Request):
        # Logique d'édition
        pass
    
    @Route("/users/{id}/delete", "user.delete", methods=["DELETE"])
    async def delete(self, id: int):
        self.repository.delete(id)
        return self.redirect("user.index")
```

## Contrôleurs API

Pour créer des APIs REST, utilisez des réponses JSON :

```python
class ApiUserController(AbstractController):
    @Route("/api/users", "api.user.list", methods=["GET"])
    async def list_users(self, page: int = 1, limit: int = 10):
        users = self.user_service.paginate(page, limit)
        return self.json({
            "data": users,
            "pagination": {
                "page": page,
                "limit": limit
            }
        })
    
    @Route("/api/users/{id}", "api.user.get", methods=["GET"])
    async def get_user(self, id: int):
        user = self.user_service.find(id)
        if not user:
            return self.json({"error": "User not found"}, status_code=404)
        return self.json({"data": user})
```

## Gestion des erreurs

### Erreurs personnalisées

```python
from fastapi import HTTPException

@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    user = self.user_repository.find(id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return self.render("user/show.html", {"user": user})
```

### Gestionnaires d'erreurs globaux

```python
from framefox.core.exception.app_exception import AppException

class UserNotFoundException(AppException):
    def __init__(self, user_id: int):
        super().__init__(f"Utilisateur {user_id} non trouvé", 404)

# Dans le contrôleur
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    user = self.user_repository.find(id)
    if not user:
        raise UserNotFoundException(id)
    return self.render("user/show.html", {"user": user})
```

## Bonnes pratiques

### Organisation du code

1. **Un contrôleur par entité** : `UserController`, `PostController`
2. **Méthodes courtes** : Déléguez la logique métier aux services
3. **Nommage cohérent** : Utilisez des conventions claires pour les routes

### Performance

```python
# Utilisez l'injection de dépendances
class UserController(AbstractController):
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    # Préférez les services pour la logique métier
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        user = self.user_service.get_user_with_posts(id)
        return self.render("user/show.html", {"user": user})
```

### Sécurité

```python
# Utilisez la validation des types
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):  # int forcé automatiquement
    # ...

# Validez les données d'entrée
from pydantic import BaseModel

class UpdateUserRequest(BaseModel):
    name: str
    email: EmailStr

@Route("/users/{id}", "user.update", methods=["PUT"])
async def update(self, id: int, data: UpdateUserRequest):
    # Données automatiquement validées
    # ...
```
