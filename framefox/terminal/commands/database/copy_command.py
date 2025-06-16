import ast
import importlib.util
import os

import psycopg2
import pymysql
from sqlmodel import create_engine

from framefox.core.config.settings import Settings
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.database_url_parser import DatabaseUrlParser

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class CopyCommand(AbstractCommand):
    def __init__(self):
        super().__init__("copy")
        settings = Settings()
        self.database_url = settings.database_url
        self.entity_directory = r"src/entity"
        self.base_model = "AbstractEntity"

    def execute(self):
        """
        Copy database tables from the entity directory to the database without using migrations.\n
        This command will create SQLModel tables based on the Python files in the specified directory.\n
        It will check if the database exists, and if not, it will inform the user to create it first.\n
        If the database exists, it will create the tables based on the SQLModel classes found in the directory.\n
        If the directory does not contain any SQLModel classes, it will inform the user.\n
        If the database already exists, it will create the tables without checking for existing tables.\n
        """
        if not CopyCommand.database_exists(self.database_url):
            self.printer.print_msg(
                "The database does not exist. Please create it first.",
                theme="error",
                linebefore=True,
            )
            self.printer.print_full_text(
                "You should try [bold green]framefox database create[/bold green]",
                newline=True,
            )
            return
        try:
            CopyCommand.create_sqlmodel_tables_from_directory(
                directory=self.entity_directory,
                database_url=self.database_url,
                base_model=self.base_model,
            )
            self.printer.print_msg(
                "Tables created successfully.",
                theme="success",
                linebefore=True,
                newline=True,
            )
            self.printer.print_full_text(
                "You should try [bold green]framefox create crud[/bold green]",
                newline=True,
            )
        except Exception as e:
            self.printer.print_msg(
                f"An error occurred: {e}",
                theme="error",
                linebefore=True,
            )
            # self.printer.print_msg(
            #     "The database does not exist. Please create it first.",
            #     theme="error",
            #     newline=True,
            # )

    @staticmethod
    def find_sqlmodel_classes_in_file(filepath, base_model):
        """
        Find SQLModel classes in a file that inherit from a given base model.

        Args:
            filepath (str): The path to the file.
            base_model (str): The name of the base model.

        Returns:
            List[str]: A list of class names that inherit from the base model.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            file_content = f.read()

        tree = ast.parse(file_content)
        sqlmodel_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == base_model:
                        sqlmodel_classes.append(node.name)

        return sqlmodel_classes

    @staticmethod
    def import_module_from_file(filepath):
        """
        Import a module from a file.

        Args:
            filepath (str): The path to the file containing the module.

        Returns:
            module: The imported module.

        Raises:
            ImportError: If the module cannot be imported.

        """
        module_name = os.path.basename(filepath).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def find_sqlmodel_classes_in_directory(directory, base_model):
        """
        Find SQLModel classes in a directory that inherit from a given base model.

        Args:
            directory (str): The path to the directory.
            base_model (str): The name of the base model.

        Returns:
            dict: A dictionary where the keys are file paths and the values are lists of class names that inherit from
                  the base model.
        """
        sqlmodel_classes_found = {}

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    classes = CopyCommand.find_sqlmodel_classes_in_file(filepath, base_model)

                    if classes:
                        sqlmodel_classes_found[filepath] = classes

        return sqlmodel_classes_found

    @staticmethod
    def create_sqlmodel_tables_from_directory(directory, database_url, base_model):
        """
        Create SQLModel tables from the Python files in the specified directory.

        Args:
            directory (str): The directory path containing the Python files.
            database_url (str): The URL of the database to connect to.
            base_model (Type[SQLModel]): The base model class for the SQLModel classes.

        Returns:
            None

        Raises:
            None
        """
        sqlmodel_classes = CopyCommand.find_sqlmodel_classes_in_directory(directory, base_model)

        if sqlmodel_classes:
            engine = create_engine(database_url, echo=True)

            for filepath, classes in sqlmodel_classes.items():
                module = CopyCommand.import_module_from_file(filepath)
                for class_name in classes:
                    class_obj = getattr(module, class_name)
                    class_obj.metadata.create_all(engine)

            print(f"Tables created for SQLModel classes found in {directory}.")
        else:
            print("No SQLModel classes found in the directory.")

    @staticmethod
    def database_exists(db_url: str) -> bool:
        """
        Check if a database exists based on its URL.
        Handles SQLite, PostgreSQL, and MySQL.
        """
        scheme, user, password, host, port, database = DatabaseUrlParser.parse(db_url)

        # SQLite
        if scheme == "sqlite":
            db_path = db_url.split(r"///")[1]
            if not db_path or db_path == ":memory:":
                return False
            return os.path.exists(db_path)

        # PostgreSQL
        elif scheme.startswith("postgresql"):
            try:
                connection = psycopg2.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    dbname="postgres",  # Connexion à la base système pour vérifier l'existence
                )
                connection.autocommit = True
                cursor = connection.cursor()
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")
                exists = cursor.fetchone() is not None

                cursor.close()
                connection.close()
                return exists
            except Exception as e:
                print(f"Erreur PostgreSQL : {e}")
                return False

        # MySQL
        elif scheme.startswith("mysql"):
            try:
                # Se connecter au serveur MySQL sans spécifier de base de données
                connection = pymysql.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=int(port) if port else 3306,
                )
                cursor = connection.cursor()
                # Vérifier si la base de données existe
                cursor.execute(f"SHOW DATABASES LIKE '{database}'")
                exists = cursor.fetchone() is not None

                cursor.close()
                connection.close()
                return exists
            except Exception as e:
                print(f"MySQL error: {e}")
                return False

        # Unsupported database type
        else:
            raise ValueError(f"Unsupported database type: {scheme}")
