from functools import wraps

from framefox.core.events.event_dispatcher import dispatcher


class DispatchEvent:
    """
    Un décorateur pour dispatcher des événements avant et après l'exécution d'une fonction/middleware.

    Args:
        event_before (str): Nom de l'événement à dispatcher avant l'exécution.
        event_after (str): Nom de l'événement à dispatcher après l'exécution.
    """

    def __init__(self, event_before: str, event_after: str):
        self.event_before = event_before
        self.event_after = event_after

    def __call__(self, func):
        @wraps(func)
        async def wrapper(middleware_instance, request, call_next):
            # Dispatcher l'événement avant avec la requête
            dispatcher.dispatch(self.event_before, {"request": request})

            # Exécuter la fonction/middleware
            response = await func(middleware_instance, request, call_next)

            # Dispatcher l'événement après avec la réponse
            dispatcher.dispatch(self.event_after, {"response": response})

            return response

        return wrapper
