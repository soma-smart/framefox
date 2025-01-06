import argparse
from src.terminal.interactive_terminal import InteractiveTerminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive Terminal")
    parser.add_argument('command', help="Command to execute")
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help="Arguments for the command")
    args = parser.parse_args()

    terminal = InteractiveTerminal()
    terminal.load_commands()
    terminal.run(args.command, args.args)
