import logging

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class WorkerPollingFilter(logging.Filter):
    """Filters repetitive SQL logs and debug logs from Pika"""

    def __init__(self):
        super().__init__()

    def filter(self, record):

        if record.name.startswith("pika.") and record.levelno < logging.ERROR:
            return False

        sql_keywords = [
            "SELECT task",
            "FROM task",
            "task.queue",
            "task.status",
            "pg_catalog.version",
            "current_schema",
            "standard_conforming_strings",
        ]

        if hasattr(record, "msg") and isinstance(record.msg, str):

            matching_keywords = [kw for kw in sql_keywords if kw in record.msg]
            if len(matching_keywords) >= 2:
                return False

        return True
