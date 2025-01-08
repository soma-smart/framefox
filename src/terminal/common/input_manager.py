class InputManager:
    @staticmethod
    def wait_input(choices: list, type: str):
        user_input = input(f"{type}: ")
        if user_input == "?":
            print("Choices:", choices)
            return InputManager.wait_input(choices, type)
        if user_input not in choices:
            print(f"Invalid {type}.")
            return InputManager.wait_input(choices, type)
        return user_input
