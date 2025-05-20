import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from framefox.core.di.service_container import ServiceContainer
from framefox.core.config.settings import Settings

class CsrfMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures the CSRF token is properly set in cookies
    for all HTML responses.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("CSRF")
        self.container = ServiceContainer()
    
    async def dispatch(self, request: Request, call_next):
        """Handles the request by automatically adding the CSRF token to the cookie."""
        
        response = await call_next(request)
        
        if not self._should_set_csrf_cookie(request, response):
            return response
        
        # Accéder directement à request.state.session_data au lieu d'utiliser Session
        # qui dépend de RequestStack.get_request()
        csrf_manager = self.container.get_by_name("CsrfTokenManager")
        
        # Récupérer le token CSRF directement de session_data
        csrf_token = None
        if hasattr(request.state, "session_data"):
            csrf_token = request.state.session_data.get("csrf_token")
        
        # S'il n'existe pas, en générer un et le stocker directement
        if not csrf_token:
            csrf_token = csrf_manager.generate_token()
            if hasattr(request.state, "session_data"):
                request.state.session_data["csrf_token"] = csrf_token
                # Marquer la session comme modifiée pour qu'elle soit sauvegardée
        
        # Définir le cookie CSRF
        cookie_manager = self.container.get_by_name("CookieManager")
        cookie_manager.set_cookie(
            response=response,
            key="csrf_token",
            value=csrf_token,
            max_age=3600,  # 1 heure
        )
        
        return response
        
    def _should_set_csrf_cookie(self, request: Request, response: Response) -> bool:
        """Determines if the CSRF cookie should be set for this request/response."""
        
        # Ignorer les requêtes non-GET (POST, etc.)
        if request.method != "GET":
            return False
            
        # Ignorer les réponses de redirection
        if response.status_code >= 300 and response.status_code < 400:
            return False
            
        # Ignorer les requêtes API
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return False
            
        # Ignorer les ressources statiques
        path = request.url.path
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot']
        if any(path.endswith(ext) for ext in static_extensions):
            return False
            
        return True