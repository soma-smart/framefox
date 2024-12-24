from typing import Optional
from src.repository.user_repository import UserRepository
from src.entity.user import User


class UserBadge:
    """
    A class used to represent a User Badge.

    Attributes
    ----------
    user_identifier : str
        A string representing the user's identifier, typically an email.

    Methods
    -------
    get_user(user_repository: UserRepository) -> Optional[User]:
        Asynchronously retrieves a user from the user repository based on the user identifier.
    """

    def __init__(self, user_identifier: str):
        self.user_identifier = user_identifier

    async def get_user(self, user_repository: UserRepository) -> Optional[User]:
        user = user_repository.find_by({"email": self.user_identifier})
        if user:
            return user[0]
        return None
