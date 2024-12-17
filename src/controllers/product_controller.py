from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route
from src.core.session.session import Session


class ProductController(AbstractController):

    @Route("/products", "get_products", methods=["GET"])
    async def get_products(self):

        print(Session.get("last_visited"))

        return self.json({"products": ["Product 1", "Product 2"]})
