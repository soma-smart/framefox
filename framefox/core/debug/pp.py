import io
import inspect
from rich.console import Console
from rich.pretty import Pretty
from rich.panel import Panel
from rich import box
from rich.table import Table

from framefox.core.debug.exception.debug_exception import DebugException


def pp(*args, **kwargs):
    """
    Affiche les arguments fournis de manière élégante dans le navigateur et arrête l'exécution du programme.

    Usage:
        pp(variable_a_debugger)
    """

    frame = inspect.currentframe()
    outer_frames = inspect.getouterframes(frame)

    caller_frame = outer_frames[1]
    caller_filename = caller_frame.filename
    caller_lineno = caller_frame.lineno
    caller_function = caller_frame.function

    buffer = io.StringIO()
    console = Console(record=True, file=buffer)

    location_info = f" `{caller_filename}`, line {
        caller_lineno}, dans `{caller_function}`"

    for arg in args:
        if isinstance(arg, list):

            table = Table(
                title="Debug Output",
                box=box.ROUNDED,
                border_style=" bold bright_yellow",
            )
            if len(arg) > 0 and isinstance(arg[0], dict):

                for key in arg[0].keys():
                    table.add_column(
                        key.capitalize(),
                        style="bright_cyan",
                        header_style="bold bright_yellow",
                    )
                for item in arg:
                    table.add_row(*[str(v) for v in item.values()])
                console.print(table)
            else:
                pretty = Pretty(arg, expand_all=True, indent_guides=True)
                panel = Panel(
                    pretty,
                    title="Debug Output",
                    border_style="bold  bright_yellow",
                    box=box.ROUNDED,
                )
                console.print(panel)
        else:

            pretty = Pretty(arg, expand_all=True, indent_guides=True)
            panel = Panel(
                pretty,
                title="Debug Output",
                border_style="bold  bright_yellow",
                box=box.ROUNDED,
            )
            console.print(panel)

    html_content = console.export_html(inline_styles=True)

    # Ajouter un style CSS personnalisé avec des couleurs plus intenses
    complete_html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Debug Output</title>
            <style>
                body {{
                    background-color: #333333;
                    color: #F0F0F0;
                    font-family: 'Fira Code', monospace;
                    padding: 20px;
                }}
                pre {{
                    background-color: #333333;
                    color: #FF0000;
                    padding: 20px;
                    border-radius: 10px;
                    overflow: auto;

                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 4px solid #FF0000;
                    padding: 15px;
                    text-align: left;
                }}
                th {{
                    background-color: #FF4500;
                    color: #FFFFFF;
                }}
                tr:nth-child(even) {{
                    background-color: #1A1A1A;
                }}
                tr:nth-child(odd) {{
                    background-color: #2E2E2E;
                }}
                .rich-panel {{
                    background-color:  #333333;
                    padding: 20px;
                    border-radius: 10px;

                }}
                .debug-location {{
                    background-color: #333333;
                    color: #FFD700;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    font-family: 'Fira Code', monospace;
                }}
            </style>
        </head>
        <body>
            <div class="debug-location"><strong>Debug file:</strong> {location_info}</div>
            {html_content}
        </body>
    </html>
    """

    raise DebugException(complete_html)
