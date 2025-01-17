from framefox.terminal.commands.abstract_command import AbstractCommand


class HelloWorldCommand(AbstractCommand):
    def __init__(self):
        super().__init__('hello_world')

    def execute(self):
        """
        Print "Hello World!" to the console.
        """
        self.printer.print_msg(
            "Hello World!",
            theme="bold_normal",
            linebefore=True,
        )
        self.printer.print_full_text(
            "You should try [bold green]framefox init[/bold green]",
            newline=True,
        )
