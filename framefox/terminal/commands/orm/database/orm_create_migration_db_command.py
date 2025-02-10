import os

from alembic import command

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.orm.database.orm_copy_db_command import OrmCopyDbCommand
from framefox.terminal.common.alembic_file_manager import AlembicFileManager


class OrmCreateMigrationDbCommand(AbstractCommand):
    def __init__(self):
        super().__init__("migration")
        self.alembic_manager = AlembicFileManager()

    def execute(self):
        """Create a new migration file with Alembic"""
        try:
            if not OrmCopyDbCommand.database_exists(
                self.alembic_manager.get_database_url()
            ):
                self.printer.print_msg(
                    "The database does not exist. Please create it first.",
                    theme="error",
                )
                return

            migration_message = self.generate_migration_message()

            self.alembic_manager.setup_files()

            alembic_cfg = self.alembic_manager.get_config()

            versions_dir = self.alembic_manager.get_versions_path()
            if not os.path.exists(versions_dir):
                os.makedirs(versions_dir)

            existing_migrations = set(os.listdir(versions_dir))

            command.revision(alembic_cfg, message=migration_message, autogenerate=True)

            new_migrations = set(os.listdir(versions_dir))
            created_migration = new_migrations - existing_migrations
            if not created_migration:
                self.printer.print_msg("No migration generated.", theme="warning")
                return

            latest_migration = created_migration.pop()
            migration_path = os.path.join(versions_dir, latest_migration)

            with open(migration_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "op." not in content:
                os.remove(migration_path)
                self.printer.print_msg(
                    "No changes detected since the last migration.", theme="warning"
                )
            else:
                self.printer.print_msg(
                    "Migration file created with Alembic.", theme="success"
                )

        except Exception as e:
            self.printer.print_msg(f"Error creating migration: {e}", theme="error")
            self.printer.print_msg(
                f"Please check your migrations or entities files", theme="error"
            )

    def generate_migration_message(self):
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_migration"
