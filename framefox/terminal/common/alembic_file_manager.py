import os
import shutil

from alembic.config import Config
from sqlmodel import create_engine

from framefox.core.config.settings import Settings


class AlembicFileManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._project_root = self._get_project_root()
            self._migrations_dir = os.path.join(self._project_root, "migrations")
            self._versions_dir = os.path.join(self._migrations_dir, "versions")
            self._templates_dir = os.path.join(
                self._project_root, "framefox", "terminal", "templates"
            )
            self._initialized = True

    def _get_project_root(self) -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    def setup_files(self) -> None:
        """Sets up the necessary directories for Alembic and copies the templates"""
        os.makedirs(self._migrations_dir, exist_ok=True)
        os.makedirs(self._versions_dir, exist_ok=True)

        script_template_src = os.path.join(self._templates_dir, "script.py.mako")
        script_template_dst = os.path.join(self._migrations_dir, "script.py.mako")
        if not os.path.exists(script_template_dst):
            shutil.copy2(script_template_src, script_template_dst)

    def cleanup_files(self) -> None:
        """Cleans up the Alembic configuration directories"""
        if os.path.exists(self._migrations_dir):
            shutil.rmtree(self._migrations_dir)

    def get_config(self) -> Config:
        """Returns a programmed Alembic configuration"""
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", self._migrations_dir)
        alembic_cfg.set_main_option("sqlalchemy.url", self.get_database_url())

        alembic_cfg.attributes["connection"] = self.get_engine_connection()
        return alembic_cfg

    def get_database_url(self) -> str:
        """Returns the database URL from the configuration settings"""

        settings = Settings()

        return settings.database_url

    def get_engine_connection(self):
        """Returns a SQLAlchemy connection if necessary"""

        engine = create_engine(self.get_database_url())
        return engine.connect()

    def get_versions_path(self) -> str:
        """Returns the path to the versions folder"""
        return self._versions_dir
