from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.request.session.session import Session

from sqlalchemy import text


class TestController(AbstractController):

    @Route("/test", "get_test", methods=["GET"])
    async def get_test(self):
        external_session = self.entity_manager.external_connection(
            "sqlite:///app.db")

        query = text('SELECT * FROM user')
        result = external_session.execute(query).mappings().all()

        return self.json(users)

    @Route("/test2", "post_test", methods=["GET"])
    async def post_test(self):
        test = Session.get("test")
        access_token = Session.get("access_token")

        return self.json({"test": test, "access_token": access_token})

    @Route("/test3", "put_test", methods=["GET"])
    async def put_test(self):
        Session.flush()

        return self.json({"products": ["Product 1", "Product 2"]})
