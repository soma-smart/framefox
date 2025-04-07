from typing import Annotated

from framefox.core.config.settings import Settings
from framefox.core.middleware.middlewares.custom_cors_middleware import \
    CustomCORSMiddleware
from framefox.core.middleware.middlewares.entity_manager_middleware import \
    EntityManagerMiddleware
from framefox.core.middleware.middlewares.firewall_middleware import \
    FirewallMiddleware
from framefox.core.middleware.middlewares.request_middleware import \
    RequestMiddleware
from framefox.core.middleware.middlewares.session_middleware import \
    SessionMiddleware

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


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

    def __init__(self, app, settings: Settings):
        self.app = app
        self.settings = settings

    def setup_middlewares(self):

        # self.app.add_middleware(HTTPSRedirectMiddleware)
        self.app.add_middleware(RequestMiddleware)
        self.app.add_middleware(EntityManagerMiddleware)

        self.app.add_middleware(FirewallMiddleware, settings=self.settings)
        self.app.add_middleware(SessionMiddleware, settings=self.settings)
        self.app.add_middleware(CustomCORSMiddleware, settings=self.settings)
