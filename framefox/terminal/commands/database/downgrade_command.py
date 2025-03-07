import typer

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import \
    AbstractDatabaseCommand


class DowngradeCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("downgrade")
        self.alembic_manager = AlembicManager()

    def execute(
        self, steps: int = 1
    ):  # Correction ici : utilisez directement une valeur par défaut
        """Rolls back migrations"""
        try:
            # Vérifier si la base de données existe
            if not self.driver.database_exists(self.connection_manager.config.database):
                self.printer.print_msg(
                    "La base de données n'existe pas. Veuillez la créer d'abord.",
                    theme="error",
                )
                return

            # Calculer la révision cible (- le nombre d'étapes)
            revision = f"-{steps}" if steps > 0 else "base"

            self.printer.print_msg(
                f"Annulation de {steps} migration{'s' if steps > 1 else ''}...",
                theme="info",
            )

            # Utiliser le gestionnaire pour exécuter le downgrade
            if self.alembic_manager.downgrade(revision):
                self.printer.print_msg(
                    f"Annulation réussie de {steps} migration{'s' if steps > 1 else ''}.",
                    theme="success",
                )
            else:
                self.printer.print_msg(
                    "L'annulation des migrations a échoué.", theme="error"
                )

        except Exception as e:
            self.printer.print_msg(
                f"Erreur lors de l'annulation des migrations : {str(e)}", theme="error"
            )
