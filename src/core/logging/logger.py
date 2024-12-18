import logging
import logging.config
import os
from colorlog import ColoredFormatter


class Logger:
    def __init__(self):
        self.configure_logging()
        # Nom par défaut pour votre application
        self.logger = logging.getLogger("Application")

    def configure_logging(self):
        log_dir = os.path.join(os.path.dirname(__file__), "../../../var/log")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")

        LOG_LEVEL = "DEBUG"

        # Formatter pour les logs colorés de l'application
        color_formatter_app = {
            "()": "colorlog.ColoredFormatter",
            "format": "%(white)s[%(reset)s%(green)sApplication%(reset)s%(white)s]%(reset)s %(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(yellow)s%(name)s%(reset)s  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            "style": "%",
        }

        # Formatter pour les logs colorés du serveur Uvicorn
        color_formatter_server = {
            "()": "colorlog.ColoredFormatter",
            "format": "%(white)s[%(reset)s%(green)sServer%(reset)s%(white)s]%(reset)s %(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            "style": "%",
        }

        # Formatter pour les logs de fichier
        file_formatter = {
            "format": "[Application] %(asctime)s | %(levelname)s | %(name)s  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

        # Configuration du logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "colored_app": color_formatter_app,
                "colored_server": color_formatter_server,
                "file": file_formatter,
            },
            "handlers": {
                "console_app": {
                    "class": "logging.StreamHandler",
                    "formatter": "colored_app",
                    "level": LOG_LEVEL,
                },
                "console_server": {
                    "class": "logging.StreamHandler",
                    "formatter": "colored_server",
                    "level": LOG_LEVEL,
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "file",
                    "level": LOG_LEVEL,
                    "filename": log_file,
                },
            },
            "root": {
                "handlers": ["console_app", "file"],
                "level": LOG_LEVEL,
            },
            "loggers": {
                # Logger de l'application
                "Application": {
                    "handlers": ["console_app", "file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                # Loggers de Uvicorn
                "uvicorn": {
                    "handlers": ["console_server", "file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console_server", "file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console_server", "file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                # Vous pouvez ajouter d'autres loggers personnalisés ici si nécessaire
            },
        }

        # Appliquer la configuration
        logging.config.dictConfig(logging_config)

    def get_logger(self, name=None):
        if name:
            return logging.getLogger(name)
        else:
            return self.logger
