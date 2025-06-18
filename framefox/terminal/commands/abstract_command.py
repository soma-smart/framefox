from framefox.terminal.common.printer import Printer
from framefox.core.di.service_container import ServiceContainer

class AbstractCommand:
    """
    Classe abstraite de base pour toutes les commandes.

    """

    def __init__(self, name=None):
        """
        Initialise la commande

        Args:
            name: Le nom de la commande (utilisé pour la convention namespace:name)
        """
        self.name = name or self.__class__.__name__.replace("Command", "").lower()
        self.printer = Printer()
        self._container = None

    def execute(self, *args, **kwargs):
        """
        Exécute la commande. Doit être implémenté par les sous-classes.

        Args:
            *args: Arguments positionnels
            **kwargs: Arguments nommés

        Returns:
            int: Code de retour (0 = succès, autre = échec)
        """
        raise NotImplementedError("Les sous-classes doivent implémenter cette méthode")

    def get_container(self):
        """Obtient le container de services (lazy loading)"""
        if self._container is None:
            self._container = ServiceContainer()
        return self._container
