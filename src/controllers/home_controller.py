from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route
from fastapi import Request
from src.core.request.session.session import Session


class HomeController(AbstractController):

    @Route("/", "show_home", methods=["GET"])
    async def show_home(self, request: Request):
        # Récupérer les cookies
        cookies = request.cookies

        # Récupérer la session

        return self.json(
            {
                "message": "Welcome to the home page!",
                "cookies": cookies,
            }
        )
