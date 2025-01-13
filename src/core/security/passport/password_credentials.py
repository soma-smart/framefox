from framefox.core.security.password.password_hasher import PasswordHasher


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
        self.password_hasher = PasswordHasher()
        self.raw_password = raw_password

    def verify(self, hashed_password: str) -> bool:
        return self.password_hasher.verify_password(self.raw_password, hashed_password)
