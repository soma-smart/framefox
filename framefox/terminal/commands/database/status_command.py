from contextlib import closing

from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import \
    AbstractDatabaseCommand


class StatusCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("status")
        self.alembic_manager = AlembicManager()

    def execute(self):
        try:
            # Affichage du statut de la base de données
            console = Console()
            console.print("")
            console.print(
                "[bold orange1]État de la base de données[/bold orange1]")
            console.print("")

            # Table pour l'état de la connexion
            db_table = Table(show_header=True, header_style="bold orange1")
            db_table.add_column("Composant", style="bold orange3")
            db_table.add_column("Statut", style="white")
            db_table.add_column("Détails", style="white")

            # Récupérer les informations de connexion
            db_name = self.connection_manager.config.database
            db_exists = self.driver.database_exists(db_name)

            # Ligne pour l'existence de la base de données
            db_table.add_row(
                "Base de données",
                "[green]Existe[/green]" if db_exists else "[red]N'existe pas[/red]",
                db_name
            )

            # Tester la connexion
            connection_ok = False
            error_message = ""

            if db_exists:
                try:
                    engine = create_engine(
                        self.alembic_manager.get_database_url_string())
                    with engine.connect() as connection:
                        connection_ok = True
                except Exception as e:
                    error_message = str(e)

            # Ligne pour la connexion
            db_table.add_row(
                "Connexion",
                "[green]Établie[/green]" if connection_ok else "[red]Échec[/red]",
                error_message if error_message else (
                    "OK" if connection_ok else "Non connecté")
            )

            # Afficher les détails de la base de données
            if db_exists and connection_ok:
                driver_name = self.connection_manager.config.driver
                host = self.connection_manager.config.host
                port = self.connection_manager.config.port

                db_table.add_row(
                    "Type",
                    f"[cyan]{driver_name.upper()}[/cyan]",
                    f"{host}:{port}"
                )

            console.print(db_table)
            console.print("")

            # Si la base de données n'existe pas, on s'arrête ici
            if not db_exists:
                self.printer.print_msg(
                    "La base de données n'existe pas. Veuillez exécuter 'framefox database:create' d'abord.",
                    theme="error",
                )
                return

            # Si la connexion a échoué, on s'arrête ici
            if not connection_ok:
                self.printer.print_msg(
                    f"Impossible de se connecter à la base de données: {error_message}",
                    theme="error",
                )
                return

            # ---- Code existant pour les migrations ----
            alembic_cfg = self.alembic_manager.create_config()
            script = ScriptDirectory.from_config(alembic_cfg)

            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()

                heads = script.get_revisions("heads")
                head_rev = heads[0].revision if heads else None

                table = Table(show_header=True, header_style="bold orange1")
                table.add_column("Version", style="cyan")
                table.add_column("Description", style="white")
                table.add_column("Status", style="green")

                rows = []
                for rev in script.walk_revisions():
                    if current_rev is None:
                        status = "PENDING"
                    else:
                        status = (
                            "CURRENT"
                            if rev.revision == current_rev
                            else (
                                "PENDING"
                                if rev.revision
                                in [
                                    r.revision
                                    for r in script.iterate_revisions(
                                        current_rev, "head"
                                    )
                                ]
                                else "APPLIED"
                            )
                        )
                    rows.append((rev.revision, rev.doc or "", status))

                console.print("[bold orange1]Migration Status[/bold orange1]")
                console.print("")

                for row in rows:
                    table.add_row(*row)

                console.print(table)
                console.print("")

                if current_rev != head_rev:
                    if current_rev is None:
                        self.printer.print_msg(
                            "Aucune migration appliquée", theme="warning"
                        )
                    else:
                        pending = list(
                            script.iterate_revisions(current_rev, "head"))
                        self.printer.print_msg(
                            f"{len(pending)} migration(s) en attente", theme="warning"
                        )
                else:
                    self.printer.print_msg(
                        "La base de données est à jour", theme="success"
                    )

                # Une fois terminé, nettoyer les fichiers temporaires
                self.alembic_manager.cleanup_temp_files()

        except Exception as e:
            self.printer.print_msg(
                f"Erreur lors de la vérification des migrations: {str(e)}",
                theme="error",
            )
            # S'assurer que les fichiers temporaires sont nettoyés même en cas d'erreur
            self.alembic_manager.cleanup_temp_files()
