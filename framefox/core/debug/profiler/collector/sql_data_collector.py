import datetime
import logging
from typing import Any, Dict, Optional

from fastapi import Request, Response

from framefox.core.config.settings import Settings
from framefox.core.debug.profiler.collector.data_collector import DataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SQLDataCollector(DataCollector):
    """
    Collects and stores SQL query information during a request lifecycle.
    Captures SQL queries, their execution time, and database configuration details.
    Integrates with SQLAlchemy and SQLModel loggers to intercept SQL statements.
    """

    def __init__(self):
        super().__init__("database", "fa-database")
        self.queries = []
        self.settings = Settings()
        self.request_active = False
        self._setup_sql_handler()

    def _setup_sql_handler(self):
        class SQLHandler(logging.Handler):
            def __init__(self, collector):
                super().__init__()
                self.collector = collector

            def emit(self, record):
                if not self.collector.request_active:
                    return
                message = record.getMessage()
                if self._is_sql_query(message):
                    duration = self._extract_duration(message)
                    self.collector.add_query(message, record.created, duration=duration)

            def _is_sql_query(self, message):
                sql_keywords = [
                    "SELECT",
                    "INSERT",
                    "UPDATE",
                    "DELETE",
                    "CREATE",
                    "ALTER",
                    "BEGIN",
                    "COMMIT",
                    "ROLLBACK",
                ]
                message_upper = message.upper()
                return any(keyword in message_upper for keyword in sql_keywords)

            def _extract_duration(self, message):
                import re

                duration_patterns = [
                    r"\[generated in ([\d.]+)s\]",
                    r"\[cached since ([\d.]+)s ago\]",
                ]
                for pattern in duration_patterns:
                    match = re.search(pattern, message)
                    if match:
                        duration_sec = float(match.group(1))
                        return round(duration_sec * 1000, 2)
                return 0.0

        self.sql_handler = SQLHandler(self)
        sql_loggers = ["sqlalchemy.engine.Engine", "sqlmodel"]
        for logger_name in sql_loggers:
            logger = logging.getLogger(logger_name)
            logger.addHandler(self.sql_handler)

    def start_request(self):
        self.request_active = True
        self.queries = []

    def add_query(
        self,
        query: str,
        timestamp: float,
        parameters: Optional[Dict] = None,
        duration: Optional[float] = None,
    ):
        if not self.request_active:
            return
        clean_query = self._clean_query(query)
        query_data = {
            "query": clean_query,
            "parameters": parameters,
            "duration": duration or 0.0,
            "timestamp": timestamp,
            "formatted_time": datetime.datetime.fromtimestamp(timestamp).strftime(
                "%H:%M:%S.%f"
            )[:-3],
        }
        self.queries.append(query_data)

    def _clean_query(self, query: str) -> str:
        if query.startswith("SQL "):
            query = query[4:]
        import re

        query = re.sub(r"\s+", " ", query.strip())
        return query

    def collect(self, request: Request, response: Response) -> None:
        self.request_active = False
        total_duration = sum(q.get("duration", 0) for q in self.queries)
        db_config = self._get_database_info()
        self.data = {
            "queries": self.queries,
            "query_count": len(self.queries),
            "total_duration": round(total_duration, 2),
            "database_info": db_config,
            "average_duration": (
                round(total_duration / len(self.queries), 2) if self.queries else 0
            ),
        }

    def _get_database_info(self) -> Dict[str, Any]:
        try:
            db_config = self.settings.database_url
            safe_config = {
                "driver": getattr(db_config, "driver", "Unknown"),
                "host": getattr(db_config, "host", "localhost"),
                "port": str(getattr(db_config, "port", "N/A")),
                "database": getattr(db_config, "database", "Unknown"),
                "echo": getattr(self.settings, "database_echo", False),
            }
            username = getattr(db_config, "username", None)
            if username:
                safe_config["username"] = username
            return safe_config
        except Exception as e:
            return {
                "driver": "Unknown",
                "host": "Unknown",
                "port": "N/A",
                "database": "Unknown",
                "echo": False,
                "error": f"Could not retrieve database info: {str(e)}",
            }

    def reset(self):
        self.start_request()
        self.data = {}
