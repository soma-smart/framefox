from passlib.context import CryptContext


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
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.raw_password = raw_password

    def verify(self, hashed_password: str) -> bool:
        return self.pwd_context.verify(self.raw_password, hashed_password)
