from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route
from src.core.session.session import Session


class TestController(AbstractController):

    @Route("/test", "get_test", methods=["GET"])
    async def get_test(self):

        return self.json({"products": ["Product 1", "Product 2"]})
