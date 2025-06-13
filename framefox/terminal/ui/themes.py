"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class FramefoxTheme:
    """Framefox CLI theme constants"""

    # Colors
    PRIMARY = "orange1"
    SECONDARY = "orange3"
    ACCENT = "cyan"
    TEXT = "white"
    DIM_TEXT = "dim white"
    SUCCESS = "green"
    ERROR = "bold red"

    # Styles
    HEADER_STYLE = f"bold {PRIMARY}"
    SUBHEADER_STYLE = f"bold {SECONDARY}"
    TABLE_HEADER_STYLE = f"bold {PRIMARY}"
    COMMAND_STYLE = f"bold {SECONDARY}"
    DESCRIPTION_STYLE = TEXT
    DIM_STYLE = DIM_TEXT


class FramefoxMessages:
    """Framefox CLI messages constants"""

    HEADER_TITLE = "🦊 Framefox Framework CLI"
    HEADER_SUBTITLE = "Swift, smart, and a bit foxy"

    # Help messages
    HELP_COMMAND_DETAILS = "Run 'framefox COMMAND --help' for specific command group details"
    HELP_INIT_DETAILS = "Run 'framefox init --help' for command details"
    HELP_EXAMPLE = "Example: 'framefox server start' or 'framefox create controller'"

    # Namespace descriptions
    NAMESPACE_DESCRIPTIONS = {
        "server": "Server operations like starting or stopping the server.",
        "create": "Create various resources like entities or CRUD operations.",
        "database": "Database operations like creating or migrating databases.",
        "debug": "Debug operations like checking routes or testing security.",
        "cache": "Cache operations like clearing cache files and directories.",
        "mock": "Mock operations like generating or loading mock data.",
    }
