from __future__ import with_statement
import sys
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlmodel import SQLModel

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import your SQLModel models here
from framefox.core.config.settings import Settings

# Create configuration
config = context.config
settings = Settings()

# Set SQLAlchemy URL
db_url = settings.database_url
if not isinstance(db_url, str):
    # If it's a DatabaseConfig object, convert it to string
    driver = db_url.driver
    dialect = 'mysql+pymysql' if driver == 'mysql' else driver
    
    if driver == 'sqlite':
        db_url = f"sqlite:///{db_url.database}"
    else:
        db_url = f"{dialect}://{db_url.username}:{db_url.password}@{db_url.host}:{db_url.port}/{db_url.database}"

# Set the SQLAlchemy URL
config.set_main_option("sqlalchemy.url", str(db_url))

# Set the target metadata
target_metadata = SQLModel.metadata

# Import all entity models
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

# Import all entity models
entities_dir = os.path.join(project_root, "src", "entity")
import_entities(entities_dir)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
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