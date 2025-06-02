from rich.console import Console
from rich.theme import Theme


class Printer:
    def __init__(self):
        self.theme_dict = {
            "error": "bold red",
            "warning": "bold yellow",
            "normal": "white",
            "bold_normal": "bold white",
            "success": "bold orange1",
        }
        self.custom_theme = Theme(self.theme_dict)
        self.console = Console(theme=self.custom_theme)

    def print(self, *args, **kwargs):
        """Uses the Rich print method."""
        self.console.print(*args, **kwargs)

    def print_msg(
        self,
        message: str,
        theme: str = "normal",
        newline: bool = False,
        linebefore: bool = False,
    ):
        """
        Prints a message to the console with a specified theme and optional newline.

        Args:
            message (str): The message to be printed.
            theme (str, optional): The theme of the message. Can be "normal", "error", or "warning". Defaults to "normal".
            newline (bool, optional): Whether to print a newline after the message. Defaults to True.
            linebefore (bool, optional): Whether to print a newline before the message. Defaults to False.
        """
        if linebefore:
            self.console.print()
        if theme not in self.theme_dict.keys():
            theme = "normal"
        self.console.print(f"[{theme}]{message}[/{theme}]")
        if newline:
            self.console.print()

    def print_full_text(
        self, text: str, newline: bool = False, linebefore: bool = False
    ):
        """
        Prints the given text with optional styling and a newline.

        This method replaces specific tags in the text with styled versions
        and prints the result using the console. Optionally, it can add a
        newline after printing the text.

        Args:
            text (str): The text to be printed. It may contain tags like
                        [error] and [warning] for styling.
            newline (bool): If True, a newline is printed after the text.
                            Defaults to True.
            linebefore (bool): If True, a newline is printed before the text.
                               Defaults to False.
        """
        if linebefore:
            self.console.print()
        styled_text = (
            text.replace("[error]", "[error]")
            .replace("[/error]", "[/error]")
            .replace("[warning]", "[warning]")
            .replace("[/warning]", "[/warning]")
        )
        self.console.print(styled_text)
        if newline:
            self.console.print()
