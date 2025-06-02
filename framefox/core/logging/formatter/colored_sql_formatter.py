import logging

import colorlog

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ColoredSQLFormatter(colorlog.ColoredFormatter):
    """
    Specialized colored formatter for SQL logs.
    Unifies all SQL logger names under "Application" and applies color formatting.
    """

    def format(self, record):
        if record.name.startswith("sqlalchemy") or record.name == "sqlmodel":
            original_name = record.name
            original_msg = record.msg
            original_args = record.args

            record.name = "Application"

            try:
                if record.args:
                    formatted_message = record.msg % record.args
                else:
                    formatted_message = str(record.msg)

                if not formatted_message.startswith("SQL "):
                    if any(
                        keyword in formatted_message.upper()
                        for keyword in [
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
                    ):
                        clean_message = " ".join(formatted_message.split())
                        record.msg = f"SQL {clean_message}"
                    else:
                        record.msg = f"SQL {formatted_message}"
                else:
                    record.msg = formatted_message

                record.args = ()

            except (TypeError, ValueError):
                record.name = "Application"
                record.msg = f"SQL {original_msg}"
                record.args = original_args

        return super().format(record)
