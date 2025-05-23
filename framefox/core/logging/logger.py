import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path

from framefox.core.logging.formatter.sqlmodel_formatter import SQLModelFormatter


class Logger:
    def __init__(self):
        self.configure_logging()
        self.logger = logging.getLogger("Application")

    def configure_logging(self):

        log_dir = Path("./var/log").resolve()

        env = os.environ.get("APP_ENV", "dev")
        # date_str = datetime.now().strftime("%Y-%m-%d")

        app_log_dir = log_dir / env
        app_log_dir.mkdir(parents=True, exist_ok=True)

        app_log_file = os.path.join(app_log_dir, f"app.log")
        sql_log_file = os.path.join(app_log_dir, f"sql.log")
        request_log_file = os.path.join(app_log_dir, f"request.log")

        LOG_LEVEL = "DEBUG" if env == "dev" else "INFO"

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
        }

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
        }

        file_formatter = {
            "format": "[%(levelname)s][%(asctime)s][%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

        file_sqlmodel_formatter = {
            "()": SQLModelFormatter,
            "format": "[%(levelname)s][%(asctime)s][%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

        # Configuration complète
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "colored_app": color_formatter_app,
                "colored_server": color_formatter_server,
                "file": file_formatter,
                "file_sqlmodel": file_sqlmodel_formatter,
            },
            "handlers": {
                # Console handlers
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
                # App log file with rotation
                "app_file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "file",
                    "level": LOG_LEVEL,
                    "filename": app_log_file,
                    "when": "midnight",
                    "interval": 1,
                    "backupCount": 30,
                    "encoding": "utf8",
                },
                # SQL log file
                "sql_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file_sqlmodel",
                    "level": "WARNING",
                    "filename": sql_log_file,
                    "maxBytes": 10 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf8",
                },
                # Request log file
                "request_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "file",
                    "level": "INFO",
                    "filename": request_log_file,
                    "maxBytes": 20 * 1024 * 1024,
                    "backupCount": 10,
                    "encoding": "utf8",
                },
            },
            "root": {
                "handlers": ["console_app", "app_file"],
                "level": LOG_LEVEL,
            },
            "loggers": {
                # Application main logger
                "Application": {
                    "handlers": ["console_app", "app_file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                # Profiler logger
                "PROFILER": {
                    "handlers": ["console_app", "app_file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                # Server loggers
                "uvicorn.access": {
                    "handlers": ["console_server", "request_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console_server", "app_file"],
                    "level": LOG_LEVEL,
                    "propagate": False,
                },
                # SQL loggers
                "sqlalchemy.engine.Engine": {
                    "handlers": ["sql_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "sqlmodel": {
                    "handlers": ["sql_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                # Third party loggers
                "python_multipart": {
                    "handlers": ["app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "passlib": {
                    "handlers": ["app_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }

        # Appliquer la configuration
        logging.config.dictConfig(logging_config)

    def get_logger(self, name=None):
        """
        Obtient un logger avec le nom spécifié ou le logger application par défaut

        Args:
            name: Nom du logger (optionnel)

        Returns:
            Logger configuré pour le canal spécifié
        """
        if name:
            return logging.getLogger(name)
        else:
            return self.logger
