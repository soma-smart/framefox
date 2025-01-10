import argparse


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Interactive Terminal")
        self.parser.add_argument('command', help="Command to execute")
        self.parser.add_argument('args', nargs=argparse.REMAINDER,
                                 help="Arguments for the command")
        self.args = self.parser.parse_args()

    def get_command(self):
        return self.args.command

    def get_args(self):
        return self.args.args
