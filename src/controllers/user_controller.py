from src.core.routing.decorator.route import Route
from src.repository.user_repository import UserRepository
from src.core.controller.abstract_controller import AbstractController
from src.core.session.session import Session


class UserController(AbstractController):

    @Route("/users", "get_users", methods=["GET"])
    async def get_users(self):

        Session.set("last_visited", "/users")

        return self.render("users.html", {"title": "user list"})
