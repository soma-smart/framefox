from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController


class RoleAdminController(AbstractController):
    @Route("/role_admin", "index", methods=["GET"])
    async def index(self):
        return self.render("role_admin.html", {"controller_name":"RoleAdminController"})
