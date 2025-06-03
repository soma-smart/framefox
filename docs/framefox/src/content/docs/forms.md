---
title: Formulaires et validation
description: Créez et validez des formulaires facilement avec Framefox
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Formulaires et validation des données

Framefox propose un système de formulaires complet qui permet de définir, valider et traiter facilement les données soumises par les utilisateurs.

## Création d'un formulaire

Pour créer un formulaire dans Framefox, vous définissez une classe qui hérite de `FormType` :

<CodeBlock
  code={`from framefox.core.form.form_type import FormType
from framefox.core.form.field.text_type import TextType
from framefox.core.form.field.email_type import EmailType
from framefox.core.form.field.password_type import PasswordType

class UserType(FormType):
    def build_form(self, form_builder):
        form_builder.add("name", TextType, {
            "required": True,
            "label": "Nom complet",
            "constraints": {
                "min_length": 2,
                "max_length": 100
            }
        })
        
        form_builder.add("email", EmailType, {
            "required": True,
            "label": "Adresse e-mail"
        })
        
        form_builder.add("password", PasswordType, {
            "required": True,
            "label": "Mot de passe",
            "constraints": {
                "min_length": 8
            }
        })`}
  lang="python"
  filename="src/forms/user_type.py"
/>

## Utilisation du formulaire dans un contrôleur

Vous pouvez ensuite utiliser votre formulaire dans un contrôleur :

<CodeBlock
  code={`from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from starlette.requests import Request

from src.forms.user_type import UserType
from src.entity.user import User

class UserController(AbstractController):
    @Route("/register", "user.register", methods=["GET", "POST"])
    async def register(self, request: Request):
        # Créer une instance du formulaire
        form = self.create_form(UserType)
        
        if request.method == "POST":
            # Traiter la soumission du formulaire
            await form.handle_request(request)
            
            if form.is_valid():
                # Récupérer les données validées
                data = form.get_data()
                
                # Créer une nouvelle entité User
                user = User()
                user.name = data["name"]
                user.email = data["email"]
                user.password = self.get_service("security.password_encoder").encode(data["password"])
                
                # Sauvegarder dans la base de données
                await self.get_entity_manager().persist(user)
                await self.get_entity_manager().flush()
                
                # Rediriger vers une autre page
                return self.redirect("user.success")
        
        # Afficher le formulaire
        return self.render("user/register.html", {
            "form": form
        })`}
  lang="python"
  filename="src/controllers/user_controller.py"
/>

## Rendu du formulaire dans un template

Framefox permet un rendu facile des formulaires dans vos templates :

<CodeBlock
  code={`<!DOCTYPE html>
<html>
<head>
    <title>Inscription</title>
    <link href="{{ asset('css/style.css') }}" rel="stylesheet">
</head>
<body>
    <h1>Créer un compte</h1>
    
    <form method="POST">
        {{ csrf_token() }}
        
        <div class="form-group">
            {{ form.render_label("name") }}
            {{ form.render_field("name") }}
            {{ form.render_errors("name") }}
        </div>
        
        <div class="form-group">
            {{ form.render_label("email") }}
            {{ form.render_field("email") }}
            {{ form.render_errors("email") }}
        </div>
        
        <div class="form-group">
            {{ form.render_label("password") }}
            {{ form.render_field("password") }}
            {{ form.render_errors("password") }}
        </div>
        
        <button type="submit">S'inscrire</button>
    </form>
</body>
</html>`}
  lang="html"
  filename="templates/user/register.html"
/>

Vous pouvez également générer le formulaire entier en une seule fois :

<CodeBlock
  code={`<form method="POST">
    {{ csrf_token() }}
    {{ form.render() }}
    <button type="submit">S'inscrire</button>
</form>`}
  lang="html"
/>

## Types de champs disponibles

Framefox propose de nombreux types de champs pour vos formulaires :

| Type | Description |
|------|-------------|
| `TextType` | Champ texte simple |
| `EmailType` | Champ email avec validation |
| `PasswordType` | Champ mot de passe |
| `NumberType` | Champ numérique |
| `CheckboxType` | Case à cocher |
| `ChoiceType` | Liste déroulante |
| `MultiChoiceType` | Liste à sélection multiple |
| `TextareaType` | Zone de texte multiligne |
| `DateType` | Sélecteur de date |
| `FileType` | Upload de fichier |
| `HiddenType` | Champ caché |

## Validation personnalisée

Vous pouvez ajouter des validations personnalisées à vos formulaires :

<CodeBlock
  code={`class UserType(FormType):
    def build_form(self, form_builder):
        # ... champs du formulaire ...
        
        # Ajouter une validation personnalisée
        form_builder.add_validator(self.validate_password_strength)
    
    def validate_password_strength(self, data):
        if "password" in data and data["password"]:
            password = data["password"]
            
            # Vérifier la complexité du mot de passe
            has_uppercase = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(not c.isalnum() for c in password)
            
            if not (has_uppercase and has_digit and has_special):
                self.add_form_error(
                    "password", 
                    "Le mot de passe doit contenir au moins une majuscule, un chiffre et un caractère spécial"
                )`}
  lang="python"
/>

## Sous-formulaires et collections

Vous pouvez également imbriquer des formulaires pour gérer des données plus complexes :

<CodeBlock
  code={`from framefox.core.form.form_type import FormType
from framefox.core.form.field.text_type import TextType
from framefox.core.form.field.collection_type import CollectionType

class AddressType(FormType):
    def build_form(self, form_builder):
        form_builder.add("street", TextType, {"required": True})
        form_builder.add("city", TextType, {"required": True})
        form_builder.add("postal_code", TextType, {"required": True})
        form_builder.add("country", TextType, {"required": True})

class ProfileType(FormType):
    def build_form(self, form_builder):
        form_builder.add("first_name", TextType, {"required": True})
        form_builder.add("last_name", TextType, {"required": True})
        
        # Ajouter un sous-formulaire
        form_builder.add("address", AddressType, {"required": True})
        
        # Ajouter une collection de sous-formulaires
        form_builder.add("alternate_addresses", CollectionType, {
            "entry_type": AddressType,
            "allow_add": True,
            "allow_delete": True
        })`}
  lang="python"
/>

## Génération automatique via l'entité

Framefox peut également générer automatiquement des formulaires basés sur vos entités :

<CodeBlock
  code={`from framefox.core.form.entity_type import EntityType
from src.entity.product import Product

class ProductType(EntityType):
    def configure(self):
        # Spécifier l'entité
        self.set_entity(Product)
        
        # Exclure certains champs
        self.exclude_fields(["created_at", "updated_at"])
        
        # Personnaliser les options de champs
        self.configure_field("price", {
            "label": "Prix (€)",
            "constraints": {
                "min": 0
            }
        })`}
  lang="python"
/>

## Formulaires avec upload de fichiers

Pour gérer l'upload de fichiers, utilisez le type `FileType` :

<CodeBlock
  code={`from framefox.core.form.form_type import FormType
from framefox.core.form.field.text_type import TextType
from framefox.core.form.field.file_type import FileType

class DocumentType(FormType):
    def build_form(self, form_builder):
        form_builder.add("title", TextType, {"required": True})
        
        form_builder.add("file", FileType, {
            "required": True,
            "constraints": {
                "max_size": "5MB",  # Taille maximale
                "mime_types": ["application/pdf", "image/jpeg", "image/png"]  # Types autorisés
            }
        })`}
  lang="python"
/>

Traitement dans le contrôleur :

<CodeBlock
  code={`@Route("/upload", "document.upload", methods=["GET", "POST"])
async def upload(self, request: Request):
    form = self.create_form(DocumentType)
    
    if request.method == "POST":
        await form.handle_request(request)
        
        if form.is_valid():
            data = form.get_data()
            
            # Récupérer le fichier uploadé
            uploaded_file = data["file"]
            
            # Sauvegarder le fichier
            file_path = f"uploads/{uploaded_file.filename}"
            await self.get_service("file_storage").save(uploaded_file, file_path)
            
            # Créer un enregistrement dans la base de données
            document = Document()
            document.title = data["title"]
            document.file_path = file_path
            
            await self.get_entity_manager().persist(document)
            await self.get_entity_manager().flush()
            
            return self.redirect("document.success")
    
    return self.render("document/upload.html", {"form": form})`}
  lang="python"
/>

## Protection CSRF

Framefox intègre automatiquement une protection CSRF dans ses formulaires. Vous devez inclure le token CSRF dans vos templates :

<CodeBlock
  code={`<form method="POST">
    {{ csrf_token() }}
    <!-- champs du formulaire -->
    <button type="submit">Envoyer</button>
</form>`}
  lang="html"
/>

Le système gère automatiquement la validation du token lors de la soumission du formulaire.
