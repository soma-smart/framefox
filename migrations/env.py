from __future__ import with_statement
import sys
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlmodel import SQLModel
from framefox.core.config.settings import Settings
from framefox.terminal.common.alembic_file_manager import AlembicFileManager


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

alembic_manager = AlembicFileManager()
alembic_manager.setup_files()


config = context.config

settings = Settings()
database_url = settings.database_url


config.set_main_option("script_location", alembic_manager._migrations_dir)
config.set_main_option("sqlalchemy.url", database_url)


target_metadata = SQLModel.metadata


def import_entities(directory):
    if not os.path.exists(directory):
        print(f"Warning: Directory {directory} does not exist")
        return

    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = os.path.splitext(filename)[0]
            module_full_path = f"src.entity.{module_name}"
            try:
                __import__(module_full_path)
            except ImportError as e:
                print(f"Error importing module {module_full_path}: {e}")


entities_dir = os.path.join(project_root, "src", "entity")
import_entities(entities_dir)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()