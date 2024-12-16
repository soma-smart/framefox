from fastapi.middleware.cors import CORSMiddleware
from src.core.config.settings import Settings

settings = Settings()


class CustomCORSMiddleware(CORSMiddleware):
    def __init__(self, app):
        super().__init__(
            app,
            allow_origins=settings.cors_config.get('allow_origins', ["*"]),
            allow_credentials=settings.cors_config.get(
                'allow_credentials', True),
            allow_methods=settings.cors_config.get('allow_methods', ["*"]),
            allow_headers=settings.cors_config.get('allow_headers', ["*"]),
        )
