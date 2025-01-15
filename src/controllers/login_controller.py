from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.orm.entity_manager import EntityManager


class LoginController(AbstractController):
    def __init__(self, entityManager: EntityManager):
        self.entity_manager = entityManager

    @Route("/login", "login", methods=["GET", "POST"])
    async def login(self):

        return self.render("login.html", {})

    @Route("/logout", "logout", methods=["GET"])
    async def logout(self):

        return self.redirect("/")
