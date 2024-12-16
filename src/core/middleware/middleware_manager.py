from src.core.middleware.auth_middleware import AuthMiddleware
from src.core.middleware.custom_session_middleware import CustomSessionMiddleware
from src.core.middleware.custom_cors_middleware import CustomCORSMiddleware


class MiddlewareManager:
    def __init__(self, app, settings):
        self.app = app
        self.settings = settings

    def setup_middlewares(self):
        # Configurer CORS
        self.app.add_middleware(CustomCORSMiddleware)

        # Ajouter le middleware de session
        self.app.add_middleware(CustomSessionMiddleware,
                                settings=self.settings)

        # Configurer les middlewares d'authentification
        if self.settings.is_auth_enabled:
            self.app.add_middleware(
                AuthMiddleware, access_control=self.settings.access_control)
