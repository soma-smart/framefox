---
title: Middleware et événements
description: Utilisez les middleware et les événements pour étendre les fonctionnalités de votre application Framefox
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Middleware et événements

Framefox propose un système de middleware et d'événements puissant qui vous permet d'intervenir à différents moments du cycle de vie de votre application.

## Middleware

Les middleware permettent d'intercepter et de traiter les requêtes HTTP avant qu'elles n'atteignent vos contrôleurs, ou de modifier les réponses avant qu'elles ne soient envoyées au client.

### Création d'un middleware

Pour créer un middleware, créez une classe qui implémente l'interface `MiddlewareInterface` :

<CodeBlock
  code={`from framefox.core.middleware.middleware_interface import MiddlewareInterface
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

class LoggingMiddleware(MiddlewareInterface):
    def __init__(self, app, logger=None):
        self.app = app
        self.logger = logger or print
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            # Laisser passer les requêtes non-HTTP (WebSocket, etc.)
            await self.app(scope, receive, send)
            return
        
        # Créer un objet Request pour accéder facilement aux informations
        request = Request(scope)
        
        # Journaliser la requête entrante
        self.logger(f"Requête reçue: {request.method} {request.url.path}")
        
        # Traiter la requête et mesurer le temps de réponse
        import time
        start_time = time.time()
        
        # Continuer le traitement de la requête
        await self.app(scope, receive, send)
        
        # Journaliser après la réponse
        duration = time.time() - start_time
        self.logger(f"Réponse envoyée en {duration:.4f}s")`}
  lang="python"
  filename="src/middleware/logging_middleware.py"
/>

### Enregistrement d'un middleware

Enregistrez votre middleware dans la configuration de l'application :

<CodeBlock
  code={`# Dans config/application.yaml
application:
  middleware:
    - src.middleware.logging_middleware.LoggingMiddleware
    - src.middleware.cors_middleware.CorsMiddleware
    - src.middleware.security_middleware.SecurityMiddleware`}
  lang="yaml"
  filename="config/application.yaml"
/>

### Middleware de gestion des exceptions

Un middleware particulièrement utile est celui qui gère les exceptions :

<CodeBlock
  code={`from framefox.core.middleware.middleware_interface import MiddlewareInterface
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
import traceback
import logging

logger = logging.getLogger("app.errors")

class ErrorHandlerMiddleware(MiddlewareInterface):
    def __init__(self, app, debug=False):
        self.app = app
        self.debug = debug
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope)
        
        # Capturer et gérer les exceptions
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            # Journaliser l'erreur
            logger.error(f"Exception non gérée: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Déterminer le format de réponse (JSON ou HTML)
            is_api_request = request.url.path.startswith("/api")
            
            if is_api_request:
                # Pour les requêtes API, renvoyer une erreur JSON
                response = JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "message": str(e) if self.debug else "Une erreur est survenue",
                        "stacktrace": traceback.format_exc() if self.debug else None
                    }
                )
            else:
                # Pour les requêtes web, afficher une page d'erreur HTML
                # Utiliser le moteur de template pour générer la page d'erreur
                from framefox.core.templating.jinja_environment import create_environment
                
                env = create_environment()
                template = env.get_template("error/500.html")
                
                content = template.render({
                    "error": e,
                    "debug": self.debug,
                    "traceback": traceback.format_exc() if self.debug else None
                })
                
                response = HTMLResponse(content=content, status_code=500)
            
            # Envoyer la réponse d'erreur
            await response(scope, receive, send)`}
  lang="python"
  filename="src/middleware/error_handler_middleware.py"
/>

## Événements

Le système d'événements de Framefox permet de réagir à différentes actions qui se produisent dans votre application.

### Création d'un écouteur d'événements

Pour créer un écouteur d'événements, définissez une classe qui implémente `EventListenerInterface` :

<CodeBlock
  code={`from framefox.core.event.event_listener_interface import EventListenerInterface
from framefox.core.event.events import RequestEvent, ResponseEvent, UserLoginEvent

class SecurityEventListener(EventListenerInterface):
    def __init__(self, logger=None):
        self.logger = logger or print
    
    def get_subscribed_events(self):
        # Retourne un dictionnaire qui associe des événements à des méthodes
        return {
            UserLoginEvent: self.on_user_login,
            RequestEvent: self.on_request,
            ResponseEvent: self.on_response
        }
    
    async def on_user_login(self, event):
        # Exécuté lorsqu'un utilisateur se connecte
        user = event.get_user()
        self.logger(f"Connexion utilisateur: {user.get_username()}")
        
        # Enregistrer la connexion dans l'historique
        login_history = self.get_service("user.login_history")
        await login_history.record_login(user, event.get_request())
    
    async def on_request(self, event):
        # Exécuté pour chaque requête entrante
        request = event.get_request()
        
        # Vous pouvez ajouter des informations à la requête
        request.state.request_start_time = time.time()
    
    async def on_response(self, event):
        # Exécuté pour chaque réponse sortante
        response = event.get_response()
        request = event.get_request()
        
        # Ajouter des en-têtes de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"`}
  lang="python"
  filename="src/event/security_event_listener.py"
/>

### Enregistrement d'un écouteur d'événements

Enregistrez votre écouteur dans la configuration :

<CodeBlock
  code={`# Dans config/application.yaml
application:
  event_listeners:
    - src.event.security_event_listener.SecurityEventListener
    - src.event.analytics_event_listener.AnalyticsEventListener`}
  lang="yaml"
  filename="config/application.yaml"
/>

### Événements disponibles

Framefox fournit plusieurs événements auxquels vous pouvez réagir :

| Événement | Description |
|-----------|-------------|
| `RequestEvent` | Déclenché pour chaque requête entrante |
| `ResponseEvent` | Déclenché pour chaque réponse sortante |
| `UserLoginEvent` | Déclenché lors de la connexion d'un utilisateur |
| `UserLogoutEvent` | Déclenché lors de la déconnexion d'un utilisateur |
| `ExceptionEvent` | Déclenché lorsqu'une exception est levée |
| `EntityPrePersistEvent` | Déclenché avant la persistance d'une entité |
| `EntityPostPersistEvent` | Déclenché après la persistance d'une entité |
| `KernelBootEvent` | Déclenché au démarrage de l'application |

### Création d'événements personnalisés

Vous pouvez créer vos propres événements :

<CodeBlock
  code={`from framefox.core.event.event import Event

class OrderCompletedEvent(Event):
    def __init__(self, order, user):
        self.order = order
        self.user = user
    
    def get_order(self):
        return self.order
    
    def get_user(self):
        return self.user`}
  lang="python"
  filename="src/event/order_completed_event.py"
/>

### Émission d'événements

Vous pouvez émettre des événements depuis vos contrôleurs ou services :

<CodeBlock
  code={`from src.event.order_completed_event import OrderCompletedEvent

@Route("/checkout/complete", "checkout.complete", methods=["POST"])
async def complete_checkout(self, request: Request):
    # Traitement de la commande
    order = await self.process_order(request)
    
    # Émettre un événement
    event_dispatcher = self.get_service("event_dispatcher")
    await event_dispatcher.dispatch(OrderCompletedEvent(order, self.get_user()))`}
  lang="python"
/>

## Combinaison des middleware et événements

Les middleware et les événements peuvent être utilisés ensemble pour créer des fonctionnalités avancées :

<CodeBlock
  code={`from framefox.core.middleware.middleware_interface import MiddlewareInterface
from framefox.core.event.events import RequestEvent, ResponseEvent

class ProfilingMiddleware(MiddlewareInterface):
    def __init__(self, app, event_dispatcher=None):
        self.app = app
        self.event_dispatcher = event_dispatcher
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Émettre un événement de requête
        if self.event_dispatcher:
            await self.event_dispatcher.dispatch(RequestEvent(request))
        
        # Mesurer le temps de traitement
        import time
        start_time = time.time()
        
        # Intercepter la réponse
        original_send = send
        
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                
                # Créer une réponse pour l'événement
                from starlette.responses import Response
                response = Response(
                    content=b"",
                    status_code=message["status"],
                    headers=message.get("headers", [])
                )
                
                # Ajouter le temps de traitement aux en-têtes
                response.headers["X-Processing-Time"] = f"{duration:.4f}s"
                
                # Remplacer les en-têtes dans le message
                message["headers"] = [
                    [key.encode(), value.encode()] 
                    for key, value in response.headers.items()
                ]
                
                # Émettre un événement de réponse
                if self.event_dispatcher:
                    await self.event_dispatcher.dispatch(ResponseEvent(response, request))
            
            # Envoyer le message modifié
            await original_send(message)
        
        # Exécuter l'application avec notre send intercepté
        await self.app(scope, receive, wrapped_send)`}
  lang="python"
  filename="src/middleware/profiling_middleware.py"
/>

## Exemples d'utilisation

### Middleware d'authentification API

<CodeBlock
  code={`from framefox.core.middleware.middleware_interface import MiddlewareInterface
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt

class ApiAuthMiddleware(MiddlewareInterface):
    def __init__(self, app, secret_key):
        self.app = app
        self.secret_key = secret_key
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        
        # Vérifier si c'est une requête API
        if not request.url.path.startswith("/api/"):
            # Pas une requête API, laisser passer
            await self.app(scope, receive, send)
            return
        
        # Exclure les routes publiques
        public_routes = ["/api/token", "/api/register", "/api/public"]
        if any(request.url.path.startswith(route) for route in public_routes):
            await self.app(scope, receive, send)
            return
        
        # Vérifier le token d'authentification
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            # Pas de token, refuser l'accès
            response = JSONResponse(
                status_code=401,
                content={"error": "Authentification requise"}
            )
            await response(scope, receive, send)
            return
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Vérifier et décoder le token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Ajouter les informations d'utilisateur à la requête
            request.state.user_id = payload.get("user_id")
            request.state.user_roles = payload.get("roles", [])
            
            # Continuer le traitement
            await self.app(scope, receive, send)
            
        except jwt.ExpiredSignatureError:
            response = JSONResponse(
                status_code=401,
                content={"error": "Token expiré"}
            )
            await response(scope, receive, send)
            
        except jwt.InvalidTokenError:
            response = JSONResponse(
                status_code=401,
                content={"error": "Token invalide"}
            )
            await response(scope, receive, send)`}
  lang="python"
  filename="src/middleware/api_auth_middleware.py"
/>

### Écouteur d'événements pour l'audit

<CodeBlock
  code={`from framefox.core.event.event_listener_interface import EventListenerInterface
from framefox.core.event.events import EntityPostPersistEvent, EntityPostUpdateEvent, EntityPostDeleteEvent
import json
import datetime

class AuditEventListener(EventListenerInterface):
    def __init__(self, entity_manager=None):
        self.entity_manager = entity_manager
    
    def get_subscribed_events(self):
        return {
            EntityPostPersistEvent: self.on_entity_change,
            EntityPostUpdateEvent: self.on_entity_change,
            EntityPostDeleteEvent: self.on_entity_delete
        }
    
    async def on_entity_change(self, event):
        entity = event.get_entity()
        
        # Ignorer certaines entités pour l'audit
        if entity.__class__.__name__ in ["AuditLog", "Session"]:
            return
        
        # Créer un enregistrement d'audit
        audit = AuditLog()
        audit.entity_type = entity.__class__.__name__
        audit.entity_id = getattr(entity, "id", None)
        audit.action = event.__class__.__name__.replace("EntityPost", "").upper()
        audit.data = json.dumps(self.get_entity_data(entity))
        audit.user_id = self.get_current_user_id()
        audit.created_at = datetime.datetime.now()
        
        # Persister l'audit
        if self.entity_manager:
            await self.entity_manager.persist(audit)
            await self.entity_manager.flush()
    
    async def on_entity_delete(self, event):
        # Similaire à on_entity_change mais pour les suppressions
        pass
    
    def get_entity_data(self, entity):
        # Extraire les données pertinentes de l'entité
        data = {}
        for attr in dir(entity):
            if not attr.startswith("_") and not callable(getattr(entity, attr)):
                value = getattr(entity, attr)
                if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                    data[attr] = value
        return data
    
    def get_current_user_id(self):
        # Récupérer l'ID de l'utilisateur actuel
        try:
            from framefox.core.security.token_storage import get_token_storage
            token = get_token_storage().get_token()
            if token:
                return token.get_user().id
        except:
            pass
        return None`}
  lang="python"
  filename="src/event/audit_event_listener.py"
/>

Les middleware et les événements sont des outils puissants qui vous permettent d'ajouter des fonctionnalités transversales à votre application Framefox sans modifier vos contrôleurs ou vos modèles.
