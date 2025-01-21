from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController


class VisitorController(AbstractController):
    @Route("/visitor", "index", methods=["GET"])
    async def index(self):
        return self.render("visitor.html", {"controller_name":"VisitorController"})
