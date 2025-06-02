import secrets

from fastapi import Request

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CsrfTokenManager:
    """
    A class to manage CSRF tokens.

    Attributes:
        prefix (str): The prefix to be used for the CSRF token.

    Methods:
        generate_token() -> str:
            Generates a new CSRF token with the specified prefix.

        get_token() -> str:
            Returns the current CSRF token.

        validate_token(request: Request) -> bool:
            Retrieves the CSRF token from cookies and form data in the request and validates them.
    """

    def __init__(self, prefix: str = "csrf_"):
        self.prefix = prefix

    def generate_token(self) -> str:
        return f"{self.prefix}{secrets.token_urlsafe(32)}"

    def get_token(self) -> str:
        return self.generate_token()

    async def validate_token(self, request: Request) -> bool:
        csrf_token_cookie = request.cookies.get("csrf_token")
        form = await request.form()
        csrf_token_form = form.get("csrf_token")

        if csrf_token_cookie is None or csrf_token_form is None:
            return False

        return secrets.compare_digest(str(csrf_token_cookie), str(csrf_token_form))
