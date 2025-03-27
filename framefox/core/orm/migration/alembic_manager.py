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
            self._templates_dir = (
                self._project_root / "framefox" / "core" / "migration" / "templates"
            )
            self._initialized = True
            self._temp_files = []

    def setup_directories(self) -> None:
        """Creates necessary directories for Alembic"""
        os.makedirs(self._migrations_dir, exist_ok=True)
        os.makedirs(self._versions_dir, exist_ok=True)

    def setup_templates(self) -> None:
        """Copies necessary template files"""
        script_template_dst = self._migrations_dir / "script.py.mako"
        if not script_template_dst.exists():
            script_template_src = self._templates_dir / "script.py.mako"
            if script_template_src.exists():
                shutil.copy2(str(script_template_src),
                             str(script_template_dst))

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

    def create_migration(
        self, message: str, autogenerate: bool = True
    ) -> Optional[str]:
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
                    current = conn.execute(
                        text("SELECT version_num FROM alembic_version")
                    ).scalar()
                except Exception:
                    current = None
            config = self.create_config()
            command.upgrade(config, revision)
            with create_engine(self.get_database_url_string()).connect() as conn:
                new = conn.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar()
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
        """Deletes all migration files"""
        if os.path.exists(self._migrations_dir):
            shutil.rmtree(self._migrations_dir)
