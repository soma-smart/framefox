import time

from sqlalchemy import event
from sqlalchemy.engine import Engine

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SQLInterceptor:
    """
    Interceptor to automatically capture SQL queries
    and forward them to the profiler.
    """

    def __init__(self):
        self.query_start_time = {}
        self.setup_sqlalchemy_events()

    def setup_sqlalchemy_events(self):
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            context._query_start_time = time.time()

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            start_time = getattr(context, "_query_start_time", time.time())
            duration = (time.time() - start_time) * 1000

            try:
                from framefox.core.debug.profiler.profiler import Profiler

                profiler = Profiler()
                sql_collector = profiler.get_collector("database")

                if sql_collector:
                    formatted_params = None
                    if parameters:
                        try:
                            if isinstance(parameters, (list, tuple)) and parameters:
                                formatted_params = str(parameters)
                            elif isinstance(parameters, dict) and parameters:
                                formatted_params = str(parameters)
                        except Exception:
                            formatted_params = "Could not format parameters"

                    sql_collector.add_query(
                        query=statement,
                        timestamp=start_time,
                        parameters=formatted_params,
                        duration=round(duration, 2),
                    )
            except Exception as e:
                raise RuntimeError(f"Failed to log SQL query: {e}") from e

    @staticmethod
    def initialize():
        """Initializes the SQL interceptor."""
        return SQLInterceptor()
