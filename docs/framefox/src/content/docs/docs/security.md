---
title: Authentification et sécurité
description: Implémentez l'authentification et les mécanismes de sécurité dans votre application Framefox
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Authentification et sécurité

Framefox propose un système d'authentification et de sécurité complet pour protéger votre application et gérer les utilisateurs.

## Configuration de la sécurité

La configuration de sécurité se fait dans le fichier `config/security.yaml` :

<CodeBlock
  code={`security:
  firewalls:
    main:
      pattern: ^/
      authenticator: form_login
      login_path: /login
      check_path: /login_check
      default_target_path: /dashboard
      remember_me: true
      
  access_control:
    - path: ^/admin
      roles: [ROLE_ADMIN]
    - path: ^/profile
      roles: [ROLE_USER]
    - path: ^/api
      roles: [ROLE_API_USER]
      
  password_hashers:
    algorithm: bcrypt
    cost: 12`}
  lang="yaml"
  filename="config/security.yaml"
/>

## Entité utilisateur

Pour implémenter l'authentification, vous devez créer une entité utilisateur qui implémente l'interface `UserInterface` :

<CodeBlock
  code={`from framefox.core.orm.entity import Entity
from framefox.core.orm.field import Column, Relation
from framefox.core.security.user.user_interface import UserInterface

class User(Entity, UserInterface):
    email = Column("string", length=180, unique=True)
    password = Column("string", length=255)
    roles = Column("json", default="[]")
    is_active = Column("boolean", default=True)
    
    # Relations
    profile = Relation("UserProfile", cascade=True)
    
    def get_username(self):
        return self.email
        
    def get_roles(self):
        return self.roles
        
    def get_password(self):
        return self.password
        
    def is_account_non_expired(self):
        return True
        
    def is_account_non_locked(self):
        return True
        
    def is_credentials_non_expired(self):
        return True
        
    def is_enabled(self):
        return self.is_active`}
  lang="python"
  filename="src/entity/user.py"
/>

## Contrôleur d'authentification

Créez un contrôleur pour gérer l'authentification :

<CodeBlock
  code={`from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from starlette.requests import Request

from src.forms.login_type import LoginType
from src.forms.registration_type import RegistrationType

class SecurityController(AbstractController):
    @Route("/login", "security.login", methods=["GET", "POST"])
    async def login(self, request: Request):
        # Rediriger si déjà connecté
        if self.is_granted("ROLE_USER"):
            return self.redirect("home.index")
            
        # Récupérer l'erreur d'authentification éventuelle
        auth_error = self.get_auth_error()
        
        # Créer le formulaire de connexion
        form = self.create_form(LoginType)
        
        return self.render("security/login.html", {
            "form": form,
            "error": auth_error
        })
        
    @Route("/login_check", "security.login_check", methods=["POST"])
    async def login_check(self):
        # Ce endpoint est géré automatiquement par le système d'authentification
        pass
        
    @Route("/register", "security.register", methods=["GET", "POST"])
    async def register(self, request: Request):
        form = self.create_form(RegistrationType)
        
        if request.method == "POST":
            await form.handle_request(request)
            
            if form.is_valid():
                data = form.get_data()
                
                # Créer un nouvel utilisateur
                user = User()
                user.email = data["email"]
                user.password = self.get_service("security.password_encoder").encode(data["password"])
                user.roles = ["ROLE_USER"]
                
                # Sauvegarder l'utilisateur
                await self.get_entity_manager().persist(user)
                await self.get_entity_manager().flush()
                
                # Connecter l'utilisateur automatiquement
                await self.login_user(user)
                
                return self.redirect("home.index")
        
        return self.render("security/register.html", {
            "form": form
        })
        
    @Route("/logout", "security.logout")
    async def logout(self):
        # La déconnexion est gérée automatiquement
        pass`}
  lang="python"
  filename="src/controllers/security_controller.py"
/>

## Formulaires d'authentification

Créez les formulaires pour la connexion et l'inscription :

<CodeBlock
  code={`from framefox.core.form.form_type import FormType
from framefox.core.form.field.text_type import TextType
from framefox.core.form.field.password_type import PasswordType
from framefox.core.form.field.checkbox_type import CheckboxType

class LoginType(FormType):
    def build_form(self, form_builder):
        form_builder.add("_username", TextType, {
            "required": True,
            "label": "Adresse e-mail"
        })
        
        form_builder.add("_password", PasswordType, {
            "required": True,
            "label": "Mot de passe"
        })
        
        form_builder.add("_remember_me", CheckboxType, {
            "required": False,
            "label": "Se souvenir de moi",
            "data": False
        })`}
  lang="python"
  filename="src/forms/login_type.py"
/>

<CodeBlock
  code={`from framefox.core.form.form_type import FormType
from framefox.core.form.field.email_type import EmailType
from framefox.core.form.field.password_type import PasswordType
from framefox.core.form.field.repeated_type import RepeatedType

class RegistrationType(FormType):
    def build_form(self, form_builder):
        form_builder.add("email", EmailType, {
            "required": True,
            "label": "Adresse e-mail"
        })
        
        form_builder.add("password", RepeatedType, {
            "type": PasswordType,
            "required": True,
            "first_options": {
                "label": "Mot de passe"
            },
            "second_options": {
                "label": "Confirmer le mot de passe"
            },
            "constraints": {
                "min_length": 8
            }
        })
        
        # Validation personnalisée
        form_builder.add_validator(self.validate_email_unique)
        
    async def validate_email_unique(self, data):
        if "email" in data and data["email"]:
            # Vérifier si l'email existe déjà
            repository = self.get_repository("User")
            user = await repository.find_one_by({"email": data["email"]})
            
            if user:
                self.add_form_error("email", "Cette adresse e-mail est déjà utilisée")`}
  lang="python"
  filename="src/forms/registration_type.py"
/>

## Templates d'authentification

Template de connexion :

<CodeBlock
  code={`{% extends 'base.html' %}

{% block title %}Connexion{% endblock %}

{% block body %}
    <div class="auth-container">
        <h1>Connexion</h1>
        
        {% if error %}
            <div class="alert alert-danger">
                {{ error }}
            </div>
        {% endif %}
        
        <form method="POST" action="{{ url_for('security.login_check') }}">
            {{ csrf_token() }}
            
            <div class="form-group">
                {{ form.render_label("_username") }}
                {{ form.render_field("_username") }}
                {{ form.render_errors("_username") }}
            </div>
            
            <div class="form-group">
                {{ form.render_label("_password") }}
                {{ form.render_field("_password") }}
                {{ form.render_errors("_password") }}
            </div>
            
            <div class="form-check">
                {{ form.render_field("_remember_me") }}
                {{ form.render_label("_remember_me") }}
            </div>
            
            <button type="submit" class="btn btn-primary">Se connecter</button>
        </form>
        
        <div class="auth-links">
            <a href="{{ url_for('security.register') }}">Créer un compte</a>
            <a href="{{ url_for('security.forgot_password') }}">Mot de passe oublié ?</a>
        </div>
    </div>
{% endblock %}`}
  lang="twig"
  filename="templates/security/login.html"
/>

## Protection des routes

Vous pouvez protéger vos routes de différentes manières :

### 1. Via la configuration

Dans `config/security.yaml`, définissez les restrictions d'accès par pattern d'URL :

<CodeBlock
  code={`security:
  # ...
  access_control:
    - path: ^/admin
      roles: [ROLE_ADMIN]
    - path: ^/profile
      roles: [ROLE_USER]`}
  lang="yaml"
/>

### 2. Dans les contrôleurs

<CodeBlock
  code={`from framefox.core.security.decorator.is_granted import IsGranted
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController

class AdminController(AbstractController):
    @IsGranted("ROLE_ADMIN")
    @Route("/admin", "admin.dashboard")
    async def dashboard(self):
        return self.render("admin/dashboard.html")
        
    @Route("/moderator", "admin.moderator")
    async def moderator_area(self):
        # Vérification manuelle des permissions
        if not self.is_granted("ROLE_MODERATOR"):
            raise self.create_access_denied_exception("Vous n'avez pas les droits suffisants.")`}
  lang="python"
  filename="src/controllers/admin_controller.py"
/>

## Utilisateur courant

Accédez à l'utilisateur connecté dans vos contrôleurs :

<CodeBlock
  code={`@Route("/profile", "user.profile")
async def profile(self):
    # Récupérer l'utilisateur connecté
    user = self.get_user()
    
    return self.render("user/profile.html", {
        "user": user
    })`}
  lang="python"
/>

Dans les templates :

<CodeBlock
  code={`<nav>
    {% if is_granted('ROLE_USER') %}
        <span>Bonjour, {{ current_user.email }}</span>
        <a href="{{ url_for('security.logout') }}">Déconnexion</a>
    {% else %}
        <a href="{{ url_for('security.login') }}">Connexion</a>
        <a href="{{ url_for('security.register') }}">Inscription</a>
    {% endif %}
</nav>`}
  lang="twig"
/>

## Gestion des rôles et permissions

Framefox prend en charge un système de rôles hiérarchiques :

<CodeBlock
  code={`security:
  role_hierarchy:
    ROLE_ADMIN: [ROLE_MODERATOR]
    ROLE_MODERATOR: [ROLE_USER]
    ROLE_USER: [ROLE_VISITOR]`}
  lang="yaml"
  filename="config/security.yaml"
/>

## Authentification API avec JWT

Pour les APIs, Framefox supporte l'authentification JWT :

<CodeBlock
  code={`security:
  firewalls:
    api:
      pattern: ^/api
      authenticator: jwt
      stateless: true
      
  jwt:
    secret_key: "%env(JWT_SECRET)%"
    token_ttl: 3600`}
  lang="yaml"
/>

Contrôleur pour l'authentification API :

<CodeBlock
  code={`@Route("/api/token", "api.token", methods=["POST"])
async def get_token(self, request: Request):
    data = await request.json()
    
    # Valider les informations d'identification
    username = data.get("username")
    password = data.get("password")
    
    user = await self.get_repository("User").find_one_by({"email": username})
    
    if not user or not self.get_service("security.password_encoder").verify(password, user.password):
        return self.json({
            "error": "Identifiants invalides"
        }, status_code=401)
    
    # Générer un token JWT
    jwt_service = self.get_service("security.jwt_manager")
    token = jwt_service.create_token({
        "user_id": user.id,
        "email": user.email,
        "roles": user.roles
    })
    
    return self.json({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email
        }
    })`}
  lang="python"
/>

## Protection CSRF

La protection CSRF est automatiquement intégrée dans Framefox. Pour l'utiliser dans vos formulaires :

<CodeBlock
  code={`<form method="POST">
    {{ csrf_token() }}
    <!-- champs du formulaire -->
    <button type="submit">Envoyer</button>
</form>`}
  lang="html"
/>

## Récupération de mot de passe

Implémentez un système de récupération de mot de passe :

<CodeBlock
  code={`@Route("/forgot-password", "security.forgot_password", methods=["GET", "POST"])
async def forgot_password(self, request: Request):
    form = self.create_form(ForgotPasswordType)
    
    if request.method == "POST":
        await form.handle_request(request)
        
        if form.is_valid():
            data = form.get_data()
            email = data["email"]
            
            # Rechercher l'utilisateur
            user = await self.get_repository("User").find_one_by({"email": email})
            
            if user:
                # Générer un token de réinitialisation
                token = self.get_service("security.token_generator").generate_token(user)
                
                # Sauvegarder le token
                user.reset_token = token
                user.reset_token_expires_at = datetime.now() + timedelta(hours=1)
                await self.get_entity_manager().flush()
                
                # Envoyer l'email
                await self.get_service("mailer").send_email(
                    to=email,
                    subject="Réinitialisation de votre mot de passe",
                    template="emails/reset_password.html",
                    context={
                        "user": user,
                        "reset_url": self.generate_url("security.reset_password", {"token": token})
                    }
                )
            
            # Toujours afficher le même message pour des raisons de sécurité
            return self.render("security/password_email_sent.html")
    
    return self.render("security/forgot_password.html", {
        "form": form
    })`}
  lang="python"
/>

## Sécurisation avancée

Framefox intègre également des protections contre d'autres vulnérabilités courantes :

- **Protection XSS** : Échappement automatique des variables dans les templates
- **Protection contre le clickjacking** : En-têtes de sécurité configurables
- **Rate limiting** : Limitation des tentatives de connexion
- **Protection CORS** : Configuration des domaines autorisés

<CodeBlock
  code={`security:
  headers:
    x_frame_options: DENY
    x_content_type_options: nosniff
    x_xss_protection: "1; mode=block"
    
  cors:
    allow_origins: ['https://example.com', 'https://api.example.com']
    allow_methods: ['GET', 'POST', 'PUT', 'DELETE']
    allow_headers: ['Content-Type', 'Authorization']
    
  rate_limiting:
    login:
      limit: 5
      period: 300  # 5 minutes`}
  lang="yaml"
  filename="config/security.yaml"
/>

## Audit de sécurité

Framefox inclut un outil d'audit de sécurité pour vérifier la configuration de votre application :

<CodeBlock
  code={`framefox security:audit`}
  lang="bash"
/>

Cet outil analyse votre configuration et fournit des recommandations pour renforcer la sécurité de votre application.
