from framefox.core.middleware.middlewares.csrf_middleware import CsrfMiddleware
from framefox.core.middleware.middlewares.custom_cors_middleware import (
    CustomCORSMiddleware,
)
from framefox.core.middleware.middlewares.entity_manager_middleware import (
    EntityManagerMiddleware,
)
from framefox.core.middleware.middlewares.exception_middleware import (
    ExceptionMiddleware,
)
from framefox.core.middleware.middlewares.firewall_middleware import FirewallMiddleware
from framefox.core.middleware.middlewares.profiler_middleware import ProfilerMiddleware
from framefox.core.middleware.middlewares.request_middleware import RequestMiddleware
from framefox.core.middleware.middlewares.session_middleware import SessionMiddleware

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
    """

    def __init__(self, app):
        self.app = app

    def setup_middlewares(self):
        self.app.add_middleware(ProfilerMiddleware)
        self.app.add_middleware(ExceptionMiddleware)

        # self.app.add_middleware(HTTPSRedirectMiddleware)
        self.app.add_middleware(RequestMiddleware)
        self.app.add_middleware(EntityManagerMiddleware)
        self.app.add_middleware(CsrfMiddleware)
        self.app.add_middleware(FirewallMiddleware)
        self.app.add_middleware(SessionMiddleware)
        self.app.add_middleware(CustomCORSMiddleware)
