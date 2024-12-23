from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route
from src.repository.user_repository import UserRepository
from src.core.security.form_login_authenticator import FormLoginAuthenticator
from fastapi import Request, Response
from pydantic import BaseModel
from typing import Optional


class LoginController(AbstractController):

    @Route("/login", "login", methods=["GET"])
    async def login(self, response: Response):

        authenticator = FormLoginAuthenticator(
            email="test@test.fr",
            password="test",
        )

        authenticated = authenticator.authenticate(response)
        if authenticated:
            return {"message": "Connexion réussie"}
        else:
            return Response(content="Identifiants invalides", status_code=401)
