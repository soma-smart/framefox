from functools import wraps

from framefox.core.events.event_dispatcher import dispatcher

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class DispatchEvent:
    """
    A decorator to dispatch events before and after the execution of a function/middleware.

    Args:
        event_before (str): Name of the event to dispatch before execution.
        event_after (str): Name of the event to dispatch after execution.
    """

    def __init__(self, event_before: str, event_after: str):
        self.event_before = event_before
        self.event_after = event_after

    def __call__(self, func):
        @wraps(func)
        async def wrapper(middleware_instance, request, call_next):
            dispatcher.dispatch(self.event_before, {"request": request})
            response = await func(middleware_instance, request, call_next)
            dispatcher.dispatch(self.event_after, {"response": response})
            return response

        return wrapper
