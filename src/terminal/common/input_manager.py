import click


class InputManager:
    @staticmethod
    def input_with_option(prompt, default=None):
        if default:
            user_input = click.prompt(prompt, default=default)
        else:
            user_input = input(f"{prompt}: ")
        return user_input

    @staticmethod
    def wait_input(input_type: str, choices: list = None, quit_on_space: bool = False, default: str = None):
        user_input = InputManager.input_with_option(input_type, default)
        if user_input == "?" and choices:
            print("Choices:", choices)
            return InputManager.wait_input(input_type, choices)
        if choices and user_input not in choices:
            print(f"Invalid {input_type}.")
            return InputManager.wait_input(input_type, choices)
        return user_input
