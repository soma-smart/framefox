from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController


class AdminController(AbstractController):
    @Route("/admin", "index", methods=["GET"])
    async def index(self):
        return self.render("admin.html", {"controller_name":"AdminController"})
