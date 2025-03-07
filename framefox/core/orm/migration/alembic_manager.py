import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional, Set

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from framefox.core.config.settings import Settings


class AlembicManager:
    """Gestionnaire centralisé pour les opérations Alembic"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Correction du chemin pour remonter correctement à la racine du projet
            self._project_root = Path(
                os.path.abspath(
                    # Ajout d'un niveau supplémentaire ../
                    os.path.join(os.path.dirname(__file__), "../../../../")
                )
            )

            # Chemins importants
            self._migrations_dir = self._project_root / "migrations"
            self._versions_dir = self._migrations_dir / "versions"
            self._templates_dir = (
                self._project_root / "framefox" / "core" / "migration" / "templates"
            )

            self._initialized = True
            self._temp_files = []  # Pour suivre les fichiers temporaires

    def setup_directories(self) -> None:
        """Crée les répertoires nécessaires pour Alembic"""
        os.makedirs(self._migrations_dir, exist_ok=True)
        os.makedirs(self._versions_dir, exist_ok=True)

    def setup_templates(self) -> None:
        """Copie les fichiers de template nécessaires"""
        # Vérifier que le répertoire des templates existe
        if not os.path.exists(self._templates_dir):
            os.makedirs(self._templates_dir, exist_ok=True)

        # Copier le template script.py.mako s'il n'existe pas déjà
        script_template_dst = self._migrations_dir / "script.py.mako"
        if not script_template_dst.exists():
            script_template_src = self._templates_dir / "script.py.mako"
            if script_template_src.exists():
                shutil.copy2(str(script_template_src), str(script_template_dst))

    def create_config(self) -> Config:
        """Crée une configuration Alembic via un fichier INI temporaire"""
        # Créer un fichier temporaire
        fd, temp_path = tempfile.mkstemp(suffix=".ini")
        os.close(fd)
        self._temp_files.append(temp_path)

        # Écrire une configuration minimale dans le fichier
        with open(temp_path, "w") as f:
            f.write(
                f"""
[alembic]
script_location = {str(self._migrations_dir)}
sqlalchemy.url = {self.get_database_url_string()}
prepend_sys_path = .
            """
            )

        # Charger la config depuis le fichier
        config = Config(temp_path)
        return config

    def get_database_url_string(self) -> str:
        """Retourne l'URL de la base de données sous forme de chaîne"""
        settings = Settings()
        db_config = settings.database_url

        # Si c'est déjà une chaîne, la retourner
        if isinstance(db_config, str):
            return db_config

        # Construire une URL à partir de l'objet DatabaseConfig
        if db_config.driver == "sqlite":
            return f"sqlite:///{db_config.database}"

        # Construire l'URL avec le bon dialecte
        dialect = "mysql+pymysql" if db_config.driver == "mysql" else db_config.driver

        # S'assurer que toutes les valeurs sont des strings
        username = str(db_config.username) if db_config.username else ""
        password = str(db_config.password) if db_config.password else ""
        host = str(db_config.host) if db_config.host else "localhost"
        port = str(db_config.port) if db_config.port else "3306"
        database = str(db_config.database) if db_config.database else ""

        return f"{dialect}://{username}:{password}@{host}:{port}/{database}"

    def create_migration(
        self, message: str, autogenerate: bool = True
    ) -> Optional[str]:
        """Crée une nouvelle migration et retourne le fichier créé"""
        # Préparation des répertoires et templates
        self.setup_directories()
        self.setup_templates()

        # Sauvegarder l'état actuel des fichiers de migration
        existing_migrations = self.get_existing_migrations()

        # Créer la configuration
        config = self.create_config()

        # Générer la migration
        command.revision(config, message=message, autogenerate=autogenerate)

        # Nettoyer les fichiers temporaires
        self.cleanup_temp_files()

        # Vérifier les nouvelles migrations
        new_migrations = self.get_existing_migrations()
        created = new_migrations - existing_migrations

        if not created:
            return None

        return list(created)[0]

    def upgrade(self, revision: str = "head") -> tuple[bool, bool]:
        """
        Applique les migrations jusqu'à la révision spécifiée

        Returns:
            tuple: (succès, migrations_appliquées)
        """
        try:
            # Récupérer l'état actuel
            with create_engine(self.get_database_url_string()).connect() as conn:
                try:
                    # Vérifier la version actuelle
                    current = conn.execute(
                        text("SELECT version_num FROM alembic_version")
                    ).scalar()
                except Exception:
                    # Table n'existe probablement pas encore
                    current = None

            # Créer la configuration et exécuter l'upgrade
            config = self.create_config()
            command.upgrade(config, revision)

            # Vérifier si des migrations ont été appliquées
            with create_engine(self.get_database_url_string()).connect() as conn:
                new = conn.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar()

            # Nettoyer les fichiers temporaires
            self.cleanup_temp_files()

            # Retourne (succès, migrations_appliquées)
            return (True, current != new)
        except Exception as e:
            print(f"Erreur lors de la mise à jour: {e}")
            self.cleanup_temp_files()
            return (False, False)

    def downgrade(self, revision: str) -> bool:
        """Annule les migrations jusqu'à la révision spécifiée"""
        try:
            config = self.create_config()
            command.downgrade(config, revision)
            self.cleanup_temp_files()
            return True
        except Exception as e:
            print(f"Erreur lors du rollback: {e}")
            self.cleanup_temp_files()
            return False

    def get_existing_migrations(self) -> Set[str]:
        """Retourne l'ensemble des fichiers de migration existants"""
        if not os.path.exists(self._versions_dir):
            return set()
        return set(os.listdir(self._versions_dir))

    def get_migration_content(self, filename: str) -> str:
        """Retourne le contenu d'un fichier de migration"""
        path = os.path.join(self._versions_dir, filename)
        if not os.path.exists(path):
            return ""

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def has_changes(self, migration_content: str) -> bool:
        """Vérifie si une migration contient des changements"""
        return "op." in migration_content

    def delete_migration(self, filename: str) -> bool:
        """Supprime un fichier de migration"""
        path = os.path.join(self._versions_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def create_alembic_version_table(self, db_url: Optional[str] = None) -> bool:
        """Crée la table alembic_version dans la base de données"""
        if not db_url:
            db_url = self.get_database_url_string()

        engine = create_engine(db_url)

        try:
            with engine.connect() as connection:
                # Détecter le type de base de données pour utiliser la bonne syntaxe
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
                else:  # postgresql ou autre
                    sql = """
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    );
                    """

                connection.execute(text(sql))
                connection.commit()
                return True
        except Exception as e:
            print(f"Erreur lors de la création de la table alembic_version: {e}")
            return False

    def cleanup_temp_files(self):
        """Nettoie les fichiers temporaires"""
        for file in self._temp_files:
            if os.path.exists(file):
                os.unlink(file)
        self._temp_files = []

    def cleanup_migrations(self):
        """Supprime tous les fichiers de migration"""
        if os.path.exists(self._migrations_dir):
            shutil.rmtree(self._migrations_dir)
