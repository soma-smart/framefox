import logging
from logging import NullHandler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class WorkerLoggerConfigurator:
    """Configure les loggers pour le contexte des workers"""

    @staticmethod
    def configure():
        null_handler = NullHandler()

        sql_loggers = [
            "SQLMODEL",
            "sqlmodel",
            "sqlalchemy",
            "sqlalchemy.engine",
            "sqlalchemy.engine.Engine",
            "sqlalchemy.orm",
            "sqlalchemy.pool",
        ]

        for logger_name in sql_loggers:
            logger = logging.getLogger(logger_name)
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
            logger.addHandler(null_handler)
            logger.setLevel(logging.CRITICAL)
            logger.propagate = False
        logging.getLogger("RABBITMQ_TRANSPORT").setLevel(logging.INFO)

        for logger_name in [
            "pika",
            "pika.adapters",
            "pika.adapters.utils",
            "pika.adapters.select_connection",
            "pika.adapters.blocking_connection",
        ]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
        worker_logger = logging.getLogger("framefox.core.task.worker_manager")
        worker_logger.setLevel(logging.INFO)

        db_logger = logging.getLogger("framefox.core.orm")
        db_logger.setLevel(logging.WARNING)
