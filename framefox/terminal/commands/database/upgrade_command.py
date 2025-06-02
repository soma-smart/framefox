from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class UpgradeCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("upgrade")
        self.alembic_manager = AlembicManager()

    def execute(self):
        """Apply all migrations to the database"""
        try:
            # Vérifier si la base de données existe
            if not self.driver.database_exists(self.connection_manager.config.database):
                self.printer.print_msg(
                    "La base de données n'existe pas. Veuillez la créer d'abord.",
                    theme="error",
                )
                return

            self.printer.print_msg("Application des migrations...", theme="info")

            # Utiliser le gestionnaire pour appliquer les migrations
            success, migrations_applied = self.alembic_manager.upgrade("head")

            if success:
                if migrations_applied:
                    self.printer.print_msg(
                        "Migrations appliquées avec succès.", theme="success"
                    )
                else:
                    self.printer.print_msg(
                        "La base de données est déjà à jour, aucune migration à appliquer.",
                        theme="info",
                    )

                self.printer.print_full_text(
                    "Vous pouvez utiliser [bold orange1]framefox database:downgrade[/bold orange1] pour annuler les migrations si nécessaire.",
                    linebefore=True,
                )
            else:
                self.printer.print_msg(
                    "L'application des migrations a échoué.", theme="error"
                )

        except Exception as e:
            self.printer.print_msg(
                f"Une erreur s'est produite lors de l'application des migrations : {str(e)}",
                theme="error",
            )
