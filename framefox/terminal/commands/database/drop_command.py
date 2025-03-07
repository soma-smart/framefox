from rich.prompt import Confirm

from framefox.terminal.commands.database.abstract_database_command import \
    AbstractDatabaseCommand


class DropCommand(AbstractDatabaseCommand):
    def execute(self):
        """Supprime la base de données configurée"""
        self.printer.print_msg("drop")

        try:
            database = self.connection_manager.config.database

            # Vérifier d'abord si la base existe
            if not self.driver.database_exists(database):
                self.printer.print_msg(
                    f"Database '{database}' does not exist", theme="warning"
                )
                return

            # Afficher les informations
            self.printer.print_msg(
                f"Database type: {self.connection_manager.config.driver}", theme="info"
            )
            self.printer.print_msg(f"Database name: {database}", theme="info")

            # Demander confirmation
            confirmed = Confirm.ask(
                "\n⚠️ [bold red]WARNING[/bold red]: You are about to drop the database. All data will be lost.\nDo you want to continue?",
                default=False,
            )

            if not confirmed:
                self.printer.print_msg("Operation cancelled.", theme="warning")
                return

            # Supprimer la base de données
            if self.driver.drop_database(database):
                self.printer.print_msg(
                    f"Database dropped successfully: {database}", theme="success"
                )
            else:
                self.printer.print_msg("Failed to drop database", theme="error")

        except Exception as e:
            self.printer.print_msg(f"Error dropping database: {str(e)}", theme="error")
