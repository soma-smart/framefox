from injectable import autowired, Autowired
from typing import Annotated
from src.core.config.settings import Settings
from src.core.middleware.middlewares.auth_middleware import AuthMiddleware
from src.core.middleware.middlewares.request_middleware import RequestMiddleware
from src.core.middleware.middlewares.custom_cors_middleware import CustomCORSMiddleware
from src.core.middleware.middlewares.custom_session_middleware import (
    CustomSessionMiddleware,
)


class MiddlewareManager:
    """
    MiddlewareManager is responsible for setting up and managing the middlewares for the application.

    Attributes:
        app: The application instance where middlewares will be added.
        settings: The settings instance containing configuration for middlewares.

    Methods:
        setup_middlewares():
            Adds the necessary middlewares to the application instance.
    """

    @autowired
    def __init__(self, app, settings: Annotated[Settings, Autowired]):
        self.app = app
        self.settings = settings

    def setup_middlewares(self):
        self.app.add_middleware(RequestMiddleware)
        self.app.add_middleware(AuthMiddleware, settings=self.settings)
        self.app.add_middleware(CustomSessionMiddleware, settings=self.settings)
        self.app.add_middleware(CustomCORSMiddleware, settings=self.settings)
