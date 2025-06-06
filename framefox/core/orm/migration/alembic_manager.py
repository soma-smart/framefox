import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Set

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from framefox.core.config.settings import Settings

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AlembicManager:
    """Central manager for Alembic operations"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._project_root = Path(os.getcwd())
            self._migrations_dir = self._project_root / "migrations"
            self._versions_dir = self._migrations_dir / "versions"
            self._templates_dir = self._project_root / "framefox" / "core" / "migration" / "templates"
            self._initialized = True
            self._temp_files = []

    def setup_directories(self) -> None:
        """Creates necessary directories for Alembic"""
        os.makedirs(self._migrations_dir, exist_ok=True)
        os.makedirs(self._versions_dir, exist_ok=True)

        # Ensure __pycache__ directory exists with .gitkeep
        pycache_dir = self._versions_dir / "__pycache__"
        pycache_dir.mkdir(exist_ok=True)
        gitkeep_file = pycache_dir / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()

    def setup_templates(self) -> None:
        """Copies necessary template files"""
        script_template_dst = self._migrations_dir / "script.py.mako"
        if not script_template_dst.exists():
            script_template_src = self._templates_dir / "script.py.mako"
            if script_template_src.exists():
                shutil.copy2(str(script_template_src), str(script_template_dst))

    def create_config(self) -> Config:
        """Creates an Alembic configuration via a temporary INI file"""
        fd, temp_path = tempfile.mkstemp(suffix=".ini")
        os.close(fd)
        self._temp_files.append(temp_path)
        with open(temp_path, "w") as f:
            f.write(
                f"""
[alembic]
script_location = {str(self._migrations_dir)}
sqlalchemy.url = {self.get_database_url_string()}
prepend_sys_path = .
            """
            )
        config = Config(temp_path)
        return config

    def get_database_url_string(self) -> str:
        """Returns the database URL as a string"""
        settings = Settings()
        db_config = settings.database_url
        if isinstance(db_config, str):
            return db_config
        if db_config.driver == "sqlite":
            return f"sqlite:///{db_config.database}"
        dialect = "mysql+pymysql" if db_config.driver == "mysql" else db_config.driver
        username = str(db_config.username) if db_config.username else ""
        password = str(db_config.password) if db_config.password else ""
        host = str(db_config.host) if db_config.host else "localhost"
        port = str(db_config.port) if db_config.port else "3306"
        database = str(db_config.database) if db_config.database else ""
        return f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    def create_migration(self, message: str, autogenerate: bool = True) -> Optional[str]:
        """Creates a new migration and returns the created file"""
        self.setup_directories()
        self.setup_templates()
        existing_migrations = self.get_existing_migrations()
        config = self.create_config()
        command.revision(config, message=message, autogenerate=autogenerate)
        self.cleanup_temp_files()
        new_migrations = self.get_existing_migrations()
        created = new_migrations - existing_migrations
        if not created:
            return None
        return list(created)[0]

    def upgrade(self, revision: str = "head") -> tuple[bool, bool]:
        """
        Applies migrations up to the specified revision

        Returns:
            tuple: (success, migrations_applied)
        """
        try:
            with create_engine(self.get_database_url_string()).connect() as conn:
                try:
                    current = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
                except Exception:
                    current = None
            config = self.create_config()
            command.upgrade(config, revision)
            with create_engine(self.get_database_url_string()).connect() as conn:
                new = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            self.cleanup_temp_files()
            return (True, current != new)
        except Exception as e:
            print(f"Error during upgrade: {e}")
            self.cleanup_temp_files()
            return (False, False)

    def downgrade(self, revision: str) -> bool:
        """Reverts migrations up to the specified revision"""
        try:
            config = self.create_config()
            command.downgrade(config, revision)
            self.cleanup_temp_files()
            return True
        except Exception as e:
            print(f"Error during rollback: {e}")
            self.cleanup_temp_files()
            return False

    def get_existing_migrations(self) -> Set[str]:
        """Returns the set of existing migration files"""
        if not os.path.exists(self._versions_dir):
            return set()
        return set(os.listdir(self._versions_dir))

    def get_migration_content(self, filename: str) -> str:
        """Returns the content of a migration file"""
        path = os.path.join(self._versions_dir, filename)
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def has_changes(self, migration_content: str) -> bool:
        """Checks if a migration contains changes"""
        return "op." in migration_content

    def delete_migration(self, filename: str) -> bool:
        """Deletes a migration file"""
        path = os.path.join(self._versions_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def create_alembic_version_table(self, db_url: Optional[str] = None) -> bool:
        """Creates the alembic_version table in the database"""
        if not db_url:
            db_url = self.get_database_url_string()
        engine = create_engine(db_url)
        try:
            with engine.connect() as connection:
                if "sqlite" in db_url:
                    sql = """
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    );
                    """
                elif "mysql" in db_url:
                    sql = """
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                else:
                    sql = """
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    );
                    """
                connection.execute(text(sql))
                connection.commit()
                return True
        except Exception as e:
            print(f"Error creating alembic_version table: {e}")
            return False

    def cleanup_temp_files(self):
        """Cleans up temporary files"""
        for file in self._temp_files:
            if os.path.exists(file):
                os.unlink(file)
        self._temp_files = []

    def cleanup_migrations(self):
        """Deletes all migration files but preserves env.py and script.py.mako"""
        if not os.path.exists(self._migrations_dir):
            return

        # Files to preserve in migrations directory
        preserve_files = {"env.py", "script.py.mako"}

        # Clean versions directory (remove all .py files except __init__.py)
        if os.path.exists(self._versions_dir):
            for file in os.listdir(self._versions_dir):
                file_path = os.path.join(self._versions_dir, file)
                if os.path.isfile(file_path):
                    # Keep __init__.py, remove all other .py files
                    if file != "__init__.py" and file.endswith(".py"):
                        os.remove(file_path)
                elif os.path.isdir(file_path) and file == "__pycache__":
                    # Clean __pycache__ directory
                    shutil.rmtree(file_path)

        # Clean migration directory root but preserve important files
        for item in os.listdir(self._migrations_dir):
            item_path = os.path.join(self._migrations_dir, item)

            if os.path.isfile(item_path):
                # Only remove files that are not in preserve list
                if item not in preserve_files:
                    os.remove(item_path)
            elif os.path.isdir(item_path):
                # Don't remove versions directory, we cleaned it above
                if item != "versions":
                    shutil.rmtree(item_path)

    def clear_alembic_version_table(self, db_url: Optional[str] = None) -> bool:
        """Clears all entries from the alembic_version table in the database"""
        if not db_url:
            db_url = self.get_database_url_string()
        engine = create_engine(db_url)
        try:
            with engine.connect() as connection:
                # Check if alembic_version table exists
                if "sqlite" in db_url:
                    check_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
                elif "mysql" in db_url:
                    check_sql = (
                        "SELECT TABLE_NAME FROM information_schema.TABLES "
                        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'alembic_version'"
                    )
                else:  # postgresql
                    check_sql = "SELECT tablename FROM pg_tables " "WHERE schemaname = 'public' AND tablename = 'alembic_version'"

                result = connection.execute(text(check_sql))

                if result.fetchone():
                    # Clear all entries from alembic_version table
                    connection.execute(text("DELETE FROM alembic_version"))
                    connection.commit()
                    return True
                else:
                    # Table doesn't exist
                    return False

        except Exception as e:
            print(f"Error clearing alembic_version table: {e}")
            return False

    def clear_all_migrations(self) -> bool:
        """Deletes all migration files and clears alembic_version table"""
        try:
            # Clear database table
            self.clear_alembic_version_table()

            # Clear migration files
            self.cleanup_migrations()

            # Recreate basic structure
            self.setup_directories()

            return True
        except Exception as e:
            print(f"Error clearing all migrations: {e}")
            return False
