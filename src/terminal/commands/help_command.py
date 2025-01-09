from src.terminal.commands.abstract_command import AbstractCommand
from src.terminal.commands.unsupported_command import UnsupportedCommand
from src.terminal.command_handler import CommandHandler

import textwrap


class HelpCommand(AbstractCommand):
    def __init__(self):
        super().__init__('help')

    def execute(self):
        handler = CommandHandler()
        handler.load_commands()

        commands = {}
        for command_name, command in sorted(handler.commands.items()):
            if command_name != UnsupportedCommand().name and command_name != self.name:
                commands[command_name] = command.execute.__doc__ or " "

        generated_help = HelpCommand.generate_help(commands)
        print(generated_help)

    @staticmethod
    def generate_help(doc_dict, max_width=160, func_column_width=20):
        """
        Generate a help-like documentation with functions and their descriptions.

        Args:
            doc_dict (dict): A dictionary with function names as keys and their docs as values.
            max_width (int): Total width of the output.
            func_column_width (int): Width of the function name column.

        Returns:
            str: Formatted documentation string.
        """
        DOUBLE_INDENT = 8
        output = []
        for func, doc in doc_dict.items():
            # Format function name column
            func_name = func.ljust(func_column_width)

            # Split the docstring into lines for manual processing
            doc_lines = doc.strip().split('\n')
            formatted_doc_lines = []

            for i, line in enumerate(doc_lines):
                # Detect leading indentation in the original docstring
                stripped_line = line.lstrip()
                indent = len(line) - len(stripped_line)

                # Define the indentation level
                if i == 0:
                    # First line starts immediately after the function name
                    initial_indent = ''
                else:
                    # Align subsequent lines with the description column, respecting original indentation
                    initial_indent = ' ' * \
                        (func_column_width + indent - DOUBLE_INDENT)

                # Wrap the line while respecting its indentation
                wrapped_line = textwrap.fill(
                    stripped_line,
                    width=max_width - func_column_width,
                    initial_indent=initial_indent,
                    subsequent_indent=initial_indent
                )
                formatted_doc_lines.append(wrapped_line)

            # Combine function name with its description
            formatted_doc = "\n".join(formatted_doc_lines)
            output.append(f"{func_name}{formatted_doc}")

        # Join all formatted documentation blocks with a blank line in between
        return "\n\n".join(output)
