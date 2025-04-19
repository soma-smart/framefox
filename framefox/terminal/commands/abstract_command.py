from framefox.terminal.common.printer import Printer


class AbstractCommand:
    """
    Classe abstraite de base pour toutes les commandes.

    """
    def __init__(self):
        self.printer = Printer()

    def execute(self, *args, **kwargs):
        """
        Exécute la commande. Doit être implémenté par les sous-classes.

        Args:
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        """
        raise NotImplementedError("Les sous-classes doivent implémenter cette méthode")