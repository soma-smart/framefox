import sys

from framefox.terminal.terminal import Terminal

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


def main():
    """
    Main entry point of the Framefox CLI application.
    """
    console = Terminal()
    return console.run()


if __name__ == "__main__":
    sys.exit(main())
else:
    app = main
