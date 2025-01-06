from src.terminal.commands.abstract_command import AbstractCommand


class CreateFileCommand(AbstractCommand):
    def __init__(self):
        super().__init__('create_file')

    def execute(self, filename):
        with open(filename, 'w') as f:
            f.write('')
        print(f"File '{filename}' created.")
