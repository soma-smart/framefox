import datetime
from typing import Any, Dict, Optional
from fastapi import Request, Response

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
    SQL profiling data collector that captures SQL queries for the profiler.
    
    This collector intercepts and stores SQL queries executed during a request,
    providing detailed information about database operations including query text,
    parameters, execution time, and database configuration.
    
    Attributes:
        name (str): Identifier for this collector type
        request_active (bool): Flag indicating if request collection is active
        queries (list): List of captured SQL queries for the current request
    """
    name = "database"

    def __init__(self):
        super().__init__("database", "fa-database")
        self.request_active = False
        self.queries = []
        
        self._setup_sql_logging()

    def _setup_sql_logging(self):
        """Setup SQL logging specifically for profiler collection."""
        import logging
        
        class ProfilerSQLHandler(logging.Handler):
            def __init__(self, collector):
                super().__init__()
                self.collector = collector
                self.setLevel(logging.INFO)

            def emit(self, record):
                if self.collector.request_active:
                    message = record.getMessage()
                    timestamp = record.created
                    
                    if self._is_sql_query(message):
                        query_info = self._parse_sql_message(message, record)
                        if query_info:
                            self.collector.add_query(
                                query_info['query'],
                                timestamp,
                                query_info.get('parameters'),
                                query_info.get('duration')
                            )

            def _is_sql_query(self, message):
                """Check if the message is a SQL query."""
                sql_keywords = [
                    "SELECT", "INSERT", "UPDATE", "DELETE", 
                    "BEGIN", "COMMIT", "ROLLBACK",
                    "CREATE", "ALTER", "DROP"
                ]
                message_upper = message.upper()
                return any(keyword in message_upper for keyword in sql_keywords)

            def _parse_sql_message(self, message, record):
                """Parse SQL message to extract query and parameters."""
                try:
                    if message.startswith("SQL "):
                        query = message[4:]
                    else:
                        query = message

                    parameters = None
                    if hasattr(record, 'args') and record.args:
                        parameters = record.args

                    duration = None
                    if "[generated in" in message:
                        import re
                        duration_match = re.search(r'\[generated in ([\d.]+)s\]', message)
                        if duration_match:
                            duration = float(duration_match.group(1)) * 1000

                    return {
                        'query': query.strip(),
                        'parameters': parameters,
                        'duration': duration
                    }
                except Exception:
                    return None

        profiler_handler = ProfilerSQLHandler(self)
        
        sql_loggers = [
            logging.getLogger("sqlalchemy.engine.Engine"),
            logging.getLogger("sqlmodel")
        ]
        
        for logger in sql_loggers:
            logger.addHandler(profiler_handler)

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
