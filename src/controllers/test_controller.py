from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route


class TestController(AbstractController):

    # @Route("/test", "get_test", methods=["GET"])
    async def get_test(self):

        return self.json({"products": ["Product 1", "Product 2"]})

    # @Route("/test2", "post_test", methods=["GET"])
    async def post_test(self):

        return self.json({"products": ["Product 1", "Product 2"]})

    # @Route("/test3", "put_test", methods=["GET"])
    async def put_test(self):

        return self.json({"products": ["Product 1", "Product 2"]})
