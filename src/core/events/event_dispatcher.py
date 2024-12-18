from typing import Callable, Dict, List, Any
import importlib
import pkgutil
import inspect


class EventDispatcher:
    def __init__(self):
        self.listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def add_listener(self, event_name: str, listener: Callable[[Any], None]):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def dispatch(self, event_name: str, payload: Any = None):
        for listener in self.listeners.get(event_name, []):
            listener(payload)

    def load_listeners(self, package: str = "src.core.events.listeners"):
        """
        Charge automatiquement tous les listeners depuis le package spécifié en POO.

        Args:
            package (str): Le chemin du package contenant les listeners.
        """
        package_module = importlib.import_module(package)
        for _, module_name, _ in pkgutil.iter_modules(package_module.__path__):
            module = importlib.import_module(f"{package}.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):

                if hasattr(obj, "register_listeners"):
                    listener_instance = obj()
                    listener_instance.register_listeners(self)


dispatcher = EventDispatcher()
