import secrets


class CsrfTokenManager:
    """
    A class to manage CSRF tokens.

    Attributes:
        prefix (str): The prefix to be used for the CSRF token.
        token (str): The generated CSRF token.

    Methods:
        generate_token() -> str:
            Generates a new CSRF token with the specified prefix.

        get_token() -> str:
            Returns the current CSRF token.
    """

    def __init__(self, prefix: str = "csrf_"):
        self.prefix = prefix
        self.token = self.generate_token()

    def generate_token(self) -> str:
        return f"{self.prefix}{secrets.token_urlsafe(32)}"

    def get_token(self) -> str:
        return self.token
