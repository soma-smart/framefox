from fastapi import Request

from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route


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
