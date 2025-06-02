import logging

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SQLModelFormatter(logging.Formatter):
    """
    Unified formatter for all SQL logs in files.
    Transforms SQL logger names to appear as "Application".
    Formats SQL queries to be single-line and prepends "SQL" to the message.
    """

    def format(self, record):
        if record.name.startswith("sqlalchemy") or record.name == "sqlmodel":
            record.name = "Application"
            try:
                message = record.getMessage()
                if not message.startswith("SQL "):
                    if any(
                        keyword in message.upper()
                        for keyword in [
                            "SELECT",
                            "INSERT",
                            "UPDATE",
                            "DELETE",
                            "CREATE",
                            "ALTER",
                        ]
                    ):
                        clean_message = " ".join(message.split())
                        record.msg = f"SQL {clean_message}"
                        record.args = ()
                    else:
                        record.msg = f"SQL {message}"
                        record.args = ()
            except Exception:
                record.msg = f"SQL {record.msg}"
        return super().format(record)
