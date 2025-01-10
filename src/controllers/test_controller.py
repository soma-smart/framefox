from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.request.session.session import Session


class TestController(AbstractController):

    @Route("/test", "get_test", methods=["GET"])
    async def get_test(self):
        Session.set("test", "test")
        return self.json({"ok": True})

    @Route("/test2", "post_test", methods=["GET"])
    async def post_test(self):
        test = Session.get("test")
        access_token = Session.get("access_token")

        return self.json({"test": test, "access_token": access_token})

    @Route("/test3", "put_test", methods=["GET"])
    async def put_test(self):
        Session.flush()

        return self.json({"products": ["Product 1", "Product 2"]})
