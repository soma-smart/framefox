from rich.prompt import Prompt


class InputManager:
    @staticmethod
    def input_with_option(prompt, default=None):
        if default:
            user_input = Prompt.ask(prompt, default=str(default))
        else:
            user_input = Prompt.ask(prompt)
        return user_input

    @staticmethod
    def wait_input(prompt: str, choices: list = None, default: str = None):
        """
        Waits for user input and validates it against provided choices.

        Parameters:
        prompt (str): The prompt to display to the user.
        choices (list, optional): A list of valid choices for the input. Defaults to None.
        default (str, optional): The default value to use if no input is provided. Defaults to None.

        Returns:
        str: The validated user input.
        """
        print()
        user_input = InputManager.input_with_option(prompt, default)
        if user_input == "?" and choices:
            print("Choices:", choices)
            return InputManager.wait_input(prompt, choices, default)
        elif user_input == "?" and not choices:
            print("No choices available.")
            return InputManager.wait_input(prompt, choices, default)
        if choices and user_input not in choices:
            print()
            print(f"Invalid {prompt.lower()}.")
            return InputManager.wait_input(prompt, choices, default)
        return user_input
