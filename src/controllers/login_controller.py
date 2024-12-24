from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route


class LoginController(AbstractController):

    @Route("/login", "login", methods=["GET", "POST"])
    async def login(self):

        return self.render("login.html", {})
