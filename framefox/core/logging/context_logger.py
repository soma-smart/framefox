import logging
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Variable de contexte pour stocker l'ID de la requête actuelle
request_id: ContextVar[str] = ContextVar("request_id", default="")
request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


class ContextLogger:
    """
    Logger avec contexte pour tracer facilement les logs d'une même requête HTTP
    """

    @staticmethod
    def set_request_id(req_id: Optional[str] = None) -> str:
        """
        Définit l'ID de la requête actuelle dans le contexte

        Args:
            req_id: ID à utiliser ou None pour en générer un nouveau

        Returns:
            L'ID de la requête
        """
        if req_id is None:
            req_id = str(uuid.uuid4())
        request_id.set(req_id)
        return req_id

    @staticmethod
    def get_request_id() -> str:
        """
        Récupère l'ID de la requête actuelle

        Returns:
            L'ID de la requête ou une chaîne vide si non défini
        """
        return request_id.get()

    @staticmethod
    def set_context_value(key: str, value: Any) -> None:
        """
        Ajoute une valeur au contexte de la requête actuelle

        Args:
            key: Nom de la valeur
            value: Valeur à stocker
        """
        context = request_context.get().copy()
        context[key] = value
        request_context.set(context)

    @staticmethod
    def get_context() -> Dict[str, Any]:
        """
        Récupère le contexte complet de la requête actuelle

        Returns:
            Dictionnaire du contexte
        """
        return request_context.get()

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Récupère un logger avec le contexte intégré

        Args:
            name: Nom du logger

        Returns:
            Logger configuré
        """
        logger = logging.getLogger(name)

        # Wrapper les méthodes de logging pour ajouter les infos de contexte
        original_debug = logger.debug
        original_info = logger.info
        original_warning = logger.warning
        original_error = logger.error
        original_critical = logger.critical

        def add_context_info(func, *args, **kwargs):
            extra = kwargs.get("extra", {})
            req_id = ContextLogger.get_request_id()
            if req_id:
                extra["request_id"] = req_id

            context = ContextLogger.get_context()
            for key, value in context.items():
                extra[key] = value

            kwargs["extra"] = extra
            return func(*args, **kwargs)

        logger.debug = lambda *args, **kwargs: add_context_info(original_debug, *args, **kwargs)
        logger.info = lambda *args, **kwargs: add_context_info(original_info, *args, **kwargs)
        logger.warning = lambda *args, **kwargs: add_context_info(original_warning, *args, **kwargs)
        logger.error = lambda *args, **kwargs: add_context_info(original_error, *args, **kwargs)
        logger.critical = lambda *args, **kwargs: add_context_info(original_critical, *args, **kwargs)

        return logger
