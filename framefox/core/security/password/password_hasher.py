from passlib.context import CryptContext


class PasswordHasher:
    """
    A class used to hash and verify passwords.

    Attributes
    ----------
    pwd_context : CryptContext
        The context used for hashing and verifying passwords.

    Methods
    -------
    hash(password: str) -> str
        Hashes the provided password.

    verify(raw_password: str, hashed_password: str) -> bool
        Verifies the raw password against the hashed password.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(raw_password, hashed_password)
