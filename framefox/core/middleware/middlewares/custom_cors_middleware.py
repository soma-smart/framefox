from fastapi.middleware.cors import CORSMiddleware
from framefox.core.config.settings import Settings

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CustomCORSMiddleware(CORSMiddleware):
    """
    CustomCORSMiddleware is a subclass of CORSMiddleware that initializes the middleware
    with custom CORS settings defined in the application's settings.

    Attributes:
        app (ASGIApp): The ASGI application instance.
        allow_origins (List[str]): List of origins that are allowed to make cross-origin requests.
        allow_credentials (bool): Whether or not to allow credentials in cross-origin requests.
        allow_methods (List[str]): List of HTTP methods that are allowed for cross-origin requests.
        allow_headers (List[str]): List of HTTP headers that are allowed for cross-origin requests.

    Args:
        app (ASGIApp): The ASGI application instance to wrap with the middleware.
    """

    def __init__(self, app):
        self.settings = Settings()
        super().__init__(
            app,
            allow_origins=self.settings.cors_config.get("allow_origins", ["*"]),
            allow_credentials=self.settings.cors_config.get("allow_credentials", True),
            allow_methods=self.settings.cors_config.get("allow_methods", ["*"]),
            allow_headers=self.settings.cors_config.get("allow_headers", ["*"]),
        )
