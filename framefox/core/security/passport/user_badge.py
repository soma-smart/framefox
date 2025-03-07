"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class UserBadge:
    """
    A class used to represent a User Badge.

    Attributes
    ----------
    user_identifier : str
        A string representing the user's identifier, typically an email.
    user_identifier_property : str
        The property used to identify the user (e.g., 'email', 'username').
    """

    def __init__(self, user_identifier: str, user_identifier_property: str = "email"):
        self.user_identifier = user_identifier
        self.user_identifier_property = user_identifier_property

    async def get_user(self, repository):
        user = repository.find_by({self.user_identifier_property: self.user_identifier})
        if user:
            return user[0]
        return None
