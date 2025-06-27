import logging

from fastapi import Request, Response

from framefox.core.debug.profiler.collector.data_collector import DataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class LogDataCollector(DataCollector):
    def __init__(self):
        super().__init__("log", "fa-list")
        self.records = []
        self._setup_handler()

    def _setup_handler(self):
        class ProfilerLogHandler(logging.Handler):
            def __init__(self, collector):
                super().__init__()
                self.collector = collector

            def emit(self, record):
                # Filtrer les requêtes SQL pour éviter les doublons avec le panel database
                if not self._is_sql_query(record):
                    self.collector.add_record(record)

            def _is_sql_query(self, record):
                """Vérifie si le log est une requête SQL"""
                # Exclure les logs SQL qui seront affichés dans le panel database
                if record.name in ["sqlalchemy.engine.Engine", "sqlmodel"]:
                    message = record.getMessage().upper()
                    sql_keywords = [
                        "BEGIN",
                        "COMMIT",
                        "SELECT",
                        "INSERT",
                        "UPDATE",
                        "DELETE",
                        "CREATE",
                        "ALTER",
                    ]
                    return any(keyword in message for keyword in sql_keywords)
                return False

        self.handler = ProfilerLogHandler(self)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.handler)

    def add_record(self, record):
        self.records.append(
            {
                "message": record.getMessage(),
                "level": record.levelname,
                "channel": record.name,
                "timestamp": record.created,
                "context": getattr(record, "context", {}),
            }
        )

    def collect(self, request: Request, response: Response) -> None:
        self.data = {
            "records": self.records,
            "count": len(self.records),
            "error_count": sum(1 for r in self.records if r["level"] in ("ERROR", "CRITICAL")),
        }

    def reset(self):
        """Remet à zéro les logs collectés pour une nouvelle requête"""
        self.records = []
        self.data = {}
