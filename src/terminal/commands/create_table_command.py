from typing import Annotated
from injectable import autowired, Autowired
from sqlmodel import create_engine, SQLModel
from src.terminal.commands.abstract_command import AbstractCommand
from src.core.config.settings import Settings


class CreateTableCommand(AbstractCommand):
    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        super().__init__('create_table')
        self.database_url = settings.database_url

    def execute(self):
        """
        Create tables in the database.
        """
        try:
            engine = create_engine(self.database_url)
            SQLModel.metadata.create_all(engine)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("The database does not exist. Please create it first.")
