from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController


class RoleUserController(AbstractController):
    @Route("/role_user", "index", methods=["GET"])
    async def index(self):
        return self.render("role_user.html", {"controller_name":"RoleUserController"})
