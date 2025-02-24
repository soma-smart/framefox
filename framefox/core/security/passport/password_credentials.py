"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class PasswordCredentials:
    """
    A class used to handle password credentials and verification.

    Attributes
    ----------
    raw_password : str
        The raw password provided by the user.
    pwd_context : CryptContext
        The context used for hashing and verifying passwords.

    Methods
    -------
    verify(hashed_password: str) -> bool
        Verifies the raw password against a hashed password.
    """

    def __init__(self, raw_password: str):
        self.raw_password = raw_password
