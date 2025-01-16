from framefox.terminal.commands.abstract_command import AbstractCommand


class TestCommand(AbstractCommand):
    def __init__(self):
        super().__init__('test:test')

    def execute(self):
        """
        Print "Hello World!" to the console.
        """
        self.printer.print_msg("Hello World!")
        self.printer.print_msg("Hello World!", theme='error')
        self.printer.print_msg("Hello World!", theme='success')
        self.printer.print_full_text(
            "Ceci est un [warning]message d'avertissement[/warning] et ceci est un [error]message d'erreur[/error]."
        )
