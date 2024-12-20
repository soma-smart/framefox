from src.core.security.token_manager import TokenManager
from src.core.config.settings import Settings
from src.repository.user_repository import UserRepository
from src.entity.user import User
from fastapi import Response
from passlib.context import CryptContext
from typing import Annotated
from injectable import autowired, Autowired
import logging


class FormLoginAuthenticator:
    @autowired
    def __init__(
        self, email: str, password: str, settings: Annotated[Settings, Autowired]
    ):
        self.email = email
        self.password = password
        self.logger = logging.getLogger("AUTH")

        self.settings = settings
        self.token_manager = TokenManager(settings)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def authenticate(self, response: Response) -> bool:
        # c'est pas a l'authentification de faire le find_by_email
        user_repository = UserRepository()
        user = user_repository.find_by({"email": self.email})[0]

        if user and self.pwd_context.verify(self.password, user.password):
            self.on_auth_success(user, response)
            return True
        else:
            self.on_auth_failure()
            return False

    def on_auth_success(self, user: User, response: Response):
        token = self.token_manager.create_token(user.id, user.roles)
        self.token_manager.add_token_to_response(response, token)
        return token

    def on_auth_failure(self):

        return "error"
