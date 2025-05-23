---
title: Services et injection de dépendances
description: Organisez votre code avec des services réutilisables et l'injection de dépendances dans Framefox
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Services et injection de dépendances

Framefox intègre un conteneur d'injection de dépendances puissant qui vous permet d'organiser votre code en services réutilisables et de gérer leurs dépendances de manière élégante.

## Principes de base

L'injection de dépendances est un modèle de conception qui permet de :

1. Découpler le code en composants indépendants
2. Faciliter les tests unitaires
3. Rendre le code plus maintenable et évolutif
4. Centraliser la configuration des services

## Définition des services

Les services sont définis dans le fichier `config/services.yaml` :

<CodeBlock
  code={`services:
  # Service simple
  mailer:
    class: src.service.mailer.MailerService
    arguments:
      - "%mailer.host%"
      - "%mailer.port%"
      - "%mailer.username%"
      - "%mailer.password%"
  
  # Service avec injection d'autres services
  user_manager:
    class: src.service.user.user_manager.UserManager
    arguments:
      - "@entity_manager"
      - "@mailer"
      - "@security.password_encoder"
  
  # Service configuré avec des méthodes
  notification_manager:
    class: src.service.notification.notification_manager.NotificationManager
    arguments:
      - "@mailer"
    calls:
      - method: set_default_sender
        arguments:
          - "noreply@example.com"
          - "Mon Application"
      - method: register_handlers
        arguments:
          - ["email", "sms", "push"]`}
  lang="yaml"
  filename="config/services.yaml"
/>

## Création d'un service

Un service est simplement une classe Python qui encapsule une fonctionnalité :

<CodeBlock
  code={`# src/service/user/user_manager.py
class UserManager:
    def __init__(self, entity_manager, mailer, password_encoder):
        self.entity_manager = entity_manager
        self.mailer = mailer
        self.password_encoder = password_encoder
    
    async def create_user(self, email, password, roles=None):
        """Crée un nouvel utilisateur et l'enregistre en base de données"""
        from src.entity.user import User
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = await self.entity_manager.get_repository(User).find_one_by({"email": email})
        if existing_user:
            raise ValueError(f"Un utilisateur avec l'email {email} existe déjà")
        
        # Créer le nouvel utilisateur
        user = User()
        user.email = email
        user.password = self.password_encoder.encode(password)
        user.roles = roles or ["ROLE_USER"]
        
        # Persister l'utilisateur
        await self.entity_manager.persist(user)
        await self.entity_manager.flush()
        
        # Envoyer un email de bienvenue
        await self.mailer.send_email(
            to=email,
            subject="Bienvenue dans notre application",
            template="emails/welcome.html",
            context={"user": user}
        )
        
        return user
    
    async def change_password(self, user, new_password):
        """Change le mot de passe d'un utilisateur"""
        user.password = self.password_encoder.encode(new_password)
        await self.entity_manager.flush()
        
        # Envoyer une notification
        await self.mailer.send_email(
            to=user.email,
            subject="Votre mot de passe a été modifié",
            template="emails/password_changed.html",
            context={"user": user}
        )
        
        return True`}
  lang="python"
  filename="src/service/user/user_manager.py"
/>

## Utilisation des services dans les contrôleurs

Vous pouvez accéder aux services depuis vos contrôleurs :

<CodeBlock
  code={`from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from starlette.requests import Request

from src.forms.user_type import UserType

class UserController(AbstractController):
    @Route("/register", "user.register", methods=["GET", "POST"])
    async def register(self, request: Request):
        form = self.create_form(UserType)
        
        if request.method == "POST":
            await form.handle_request(request)
            
            if form.is_valid():
                data = form.get_data()
                
                # Utiliser le service user_manager
                user_manager = self.get_service("user_manager")
                
                try:
                    user = await user_manager.create_user(
                        email=data["email"],
                        password=data["password"]
                    )
                    
                    # Connecter l'utilisateur
                    await self.login_user(user)
                    
                    return self.redirect("home.index")
                except ValueError as e:
                    form.add_error("email", str(e))
        
        return self.render("user/register.html", {
            "form": form
        })`}
  lang="python"
  filename="src/controllers/user_controller.py"
/>

## Services avec paramètres

Vous pouvez configurer vos services avec des paramètres définis dans `config/parameter.yaml` :

<CodeBlock
  code={`# config/parameter.yaml
parameters:
  app.name: "Mon Application Framefox"
  app.version: "1.0.0"
  app.debug: true
  
  mailer.host: "smtp.example.com"
  mailer.port: 587
  mailer.username: "user@example.com"
  mailer.password: "%env(SMTP_PASSWORD)%"  # Variable d'environnement
  
  upload.directory: "%kernel.project_dir%/public/uploads"
  upload.max_size: 10485760  # 10 Mo`}
  lang="yaml"
  filename="config/parameter.yaml"
/>

Puis utilisez ces paramètres dans `services.yaml` :

<CodeBlock
  code={`services:
  uploader:
    class: src.service.file.file_uploader.FileUploader
    arguments:
      - "%upload.directory%"
      - "%upload.max_size%"`}
  lang="yaml"
/>

## Auto-configuration des services

Framefox peut auto-configurer certains services :

<CodeBlock
  code={`services:
  # Auto-configuration
  _auto_configure:
    # Tous les services dans ce répertoire seront automatiquement enregistrés
    src.service.util.*:
      tags: ["util"]
    
    # Auto-configuration avec convention de nommage
    # Les classes qui se terminent par "Service" sont automatiquement enregistrées
    src.service.*Service:
      autowire: true`}
  lang="yaml"
/>

## Services taggés

Vous pouvez utiliser des tags pour organiser et récupérer des groupes de services :

<CodeBlock
  code={`services:
  sms_notification_handler:
    class: src.service.notification.sms_handler.SmsHandler
    tags: ["notification.handler"]
  
  email_notification_handler:
    class: src.service.notification.email_handler.EmailHandler
    tags: ["notification.handler"]
  
  push_notification_handler:
    class: src.service.notification.push_handler.PushHandler
    tags: ["notification.handler"]`}
  lang="yaml"
/>

Puis récupérez tous les services d'un tag spécifique :

<CodeBlock
  code={`class NotificationManager:
    def __init__(self):
        self.handlers = {}
    
    # Cette méthode sera appelée automatiquement par le conteneur
    def set_notification_handlers(self, handlers):
        """
        Injecte tous les services taggés 'notification.handler'
        
        Cette méthode est appelée automatiquement si configurée dans services.yaml:
        calls:
          - method: set_notification_handlers
            arguments: [!tagged notification.handler]
        """
        for handler in handlers:
            self.handlers[handler.get_type()] = handler`}
  lang="python"
/>

## Définition des services dans services.yaml :

<CodeBlock
  code={`services:
  notification_manager:
    class: src.service.notification.notification_manager.NotificationManager
    calls:
      - method: set_notification_handlers
        arguments:
          - !tagged notification.handler`}
  lang="yaml"
/>

## Services de base fournis par Framefox

Framefox fournit plusieurs services de base que vous pouvez utiliser dans votre application :

| Service | Description |
|---------|-------------|
| `entity_manager` | Gère les entités et leurs opérations |
| `event_dispatcher` | Gère l'émission et l'écoute des événements |
| `mailer` | Service d'envoi d'emails |
| `security.password_encoder` | Encode et vérifie les mots de passe |
| `security.token_storage` | Gère le token d'authentification |
| `security.authorization_checker` | Vérifie les permissions utilisateur |
| `router` | Gère les routes de l'application |
| `template_engine` | Moteur de templates |
| `logger` | Service de journalisation |
| `cache` | Système de cache |

## Exemple d'un service de paiement

<CodeBlock
  code={`# src/service/payment/payment_service.py
class PaymentService:
    def __init__(self, api_key, logger, entity_manager, event_dispatcher):
        self.api_key = api_key
        self.logger = logger
        self.entity_manager = entity_manager
        self.event_dispatcher = event_dispatcher
        self.client = None
    
    def initialize(self):
        """Initialise le client de paiement"""
        import stripe
        stripe.api_key = self.api_key
        self.client = stripe
    
    async def create_payment(self, amount, currency, customer_email, description=None):
        """Crée un paiement"""
        if not self.client:
            self.initialize()
        
        try:
            # Créer un intent de paiement
            intent = self.client.PaymentIntent.create(
                amount=int(amount * 100),  # Montant en centimes
                currency=currency,
                receipt_email=customer_email,
                description=description
            )
            
            # Enregistrer la transaction
            from src.entity.payment_transaction import PaymentTransaction
            
            transaction = PaymentTransaction()
            transaction.amount = amount
            transaction.currency = currency
            transaction.customer_email = customer_email
            transaction.description = description
            transaction.payment_id = intent.id
            transaction.status = "pending"
            
            await self.entity_manager.persist(transaction)
            await self.entity_manager.flush()
            
            return {
                "transaction_id": transaction.id,
                "payment_id": intent.id,
                "client_secret": intent.client_secret
            }
            
        except Exception as e:
            self.logger.error(f"Erreur de paiement: {str(e)}")
            raise
    
    async def handle_webhook(self, event_data):
        """Traite les événements webhook de Stripe"""
        if not self.client:
            self.initialize()
        
        event_type = event_data.get("type")
        
        # Traiter les différents types d'événements
        if event_type == "payment_intent.succeeded":
            payment_intent = event_data.get("data", {}).get("object", {})
            payment_id = payment_intent.get("id")
            
            # Mettre à jour la transaction
            repository = self.entity_manager.get_repository("PaymentTransaction")
            transaction = await repository.find_one_by({"payment_id": payment_id})
            
            if transaction:
                transaction.status = "completed"
                await self.entity_manager.flush()
                
                # Émettre un événement
                from src.event.payment_completed_event import PaymentCompletedEvent
                await self.event_dispatcher.dispatch(PaymentCompletedEvent(transaction))
        
        elif event_type == "payment_intent.payment_failed":
            # Gérer les échecs de paiement
            pass
        
        return True`}
  lang="python"
  filename="src/service/payment/payment_service.py"
/>

Configuration du service :

<CodeBlock
  code={`services:
  payment_service:
    class: src.service.payment.payment_service.PaymentService
    arguments:
      - "%payment.stripe.api_key%"
      - "@logger"
      - "@entity_manager"
      - "@event_dispatcher"
    calls:
      - method: initialize`}
  lang="yaml"
  filename="config/services.yaml"
/>

## Création de services composites

Vous pouvez créer des services qui orchestrent d'autres services :

<CodeBlock
  code={`# src/service/order/order_processor.py
class OrderProcessor:
    def __init__(self, entity_manager, payment_service, inventory_service, mailer, order_validator):
        self.entity_manager = entity_manager
        self.payment_service = payment_service
        self.inventory_service = inventory_service
        self.mailer = mailer
        self.order_validator = order_validator
    
    async def process_order(self, cart, customer, shipping_address, payment_info):
        """Traite une commande complète"""
        # Valider la commande
        validation_result = self.order_validator.validate(cart, customer)
        if not validation_result.is_valid:
            return {
                "success": False,
                "errors": validation_result.errors
            }
        
        # Vérifier la disponibilité des stocks
        for item in cart.items:
            if not await self.inventory_service.is_available(item.product_id, item.quantity):
                return {
                    "success": False,
                    "errors": [f"Produit {item.product.name} n'est plus disponible en quantité suffisante"]
                }
        
        # Créer l'entité de commande
        order = Order()
        order.customer = customer
        order.shipping_address = shipping_address
        order.status = "pending"
        
        # Ajouter les articles
        total_amount = 0
        for item in cart.items:
            order_item = OrderItem()
            order_item.product_id = item.product_id
            order_item.quantity = item.quantity
            order_item.unit_price = item.product.price
            order_item.total_price = item.product.price * item.quantity
            
            order.items.append(order_item)
            total_amount += order_item.total_price
        
        order.total_amount = total_amount
        
        # Persister la commande
        await self.entity_manager.persist(order)
        await self.entity_manager.flush()
        
        # Traiter le paiement
        payment_result = await self.payment_service.create_payment(
            amount=total_amount,
            currency="EUR",
            customer_email=customer.email,
            description=f"Commande #{order.id}"
        )
        
        # Associer le paiement à la commande
        order.payment_id = payment_result["payment_id"]
        await self.entity_manager.flush()
        
        # Réserver les stocks
        for item in cart.items:
            await self.inventory_service.reserve_stock(item.product_id, item.quantity, order.id)
        
        # Envoyer confirmation par email
        await self.mailer.send_email(
            to=customer.email,
            subject=f"Confirmation de commande #{order.id}",
            template="emails/order_confirmation.html",
            context={"order": order, "customer": customer}
        )
        
        return {
            "success": True,
            "order": order,
            "payment": payment_result
        }`}
  lang="python"
  filename="src/service/order/order_processor.py"
/>

## Test des services

L'utilisation de l'injection de dépendances facilite les tests unitaires :

<CodeBlock
  code={`# tests/service/user/test_user_manager.py
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.service.user.user_manager import UserManager
from src.entity.user import User

class TestUserManager:
    @pytest.fixture
    def entity_manager_mock(self):
        em = AsyncMock()
        # Configurer le mock du repository
        repository_mock = AsyncMock()
        repository_mock.find_one_by = AsyncMock(return_value=None)
        em.get_repository.return_value = repository_mock
        return em
    
    @pytest.fixture
    def mailer_mock(self):
        return AsyncMock()
    
    @pytest.fixture
    def password_encoder_mock(self):
        encoder = MagicMock()
        encoder.encode.return_value = "encoded_password"
        return encoder
    
    @pytest.fixture
    def user_manager(self, entity_manager_mock, mailer_mock, password_encoder_mock):
        return UserManager(entity_manager_mock, mailer_mock, password_encoder_mock)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_manager, entity_manager_mock, mailer_mock, password_encoder_mock):
        # Configurer les mocks
        entity_manager_mock.get_repository().find_one_by.return_value = None
        
        # Appeler la méthode à tester
        user = await user_manager.create_user("test@example.com", "password123")
        
        # Vérifier les résultats
        assert user.email == "test@example.com"
        assert user.password == "encoded_password"
        assert "ROLE_USER" in user.roles
        
        # Vérifier que les méthodes ont été appelées
        entity_manager_mock.persist.assert_called_once()
        entity_manager_mock.flush.assert_called_once()
        password_encoder_mock.encode.assert_called_once_with("password123")
        mailer_mock.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_manager, entity_manager_mock):
        # Configurer le mock pour simuler un utilisateur existant
        existing_user = User()
        existing_user.email = "existing@example.com"
        entity_manager_mock.get_repository().find_one_by.return_value = existing_user
        
        # Vérifier que l'exception est levée
        with pytest.raises(ValueError) as excinfo:
            await user_manager.create_user("existing@example.com", "password123")
        
        assert "existe déjà" in str(excinfo.value)`}
  lang="python"
  filename="tests/service/user/test_user_manager.py"
/>

L'utilisation de services et de l'injection de dépendances dans Framefox vous permet de créer des applications modulaires, faciles à tester et à maintenir. C'est une approche idéale pour les applications d'entreprise complexes.
