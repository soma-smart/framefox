import logging

from passlib.context import CryptContext


class PasswordHasher:
    """
    Utility class for hashing and verifying passwords.
    """

    def __init__(self):
        self.logging = logging.getLogger(__name__)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Hashes the plain password.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain password against a hashed password.

        Args:
            plain_password (str): The plain password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the password is valid, otherwise False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)
