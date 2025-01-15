from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.request.session.session import Session
from framefox.core.orm.entity_manager import EntityManager
from framefox.core.di.service_container import ServiceContainer

from sqlalchemy import text


class TestController(AbstractController):
    def __init__(self, entityManager: EntityManager):
        self.entity_manager = entityManager

    @Route("/test", "get_test", methods=["GET"])
    async def get_test(self):

        # external_session = self.entity_manager.external_connection(
        #     "sqlite:///app.db")

        # query = text('SELECT * FROM user')
        # result = external_session.execute(query).mappings().all()

        return self.json({"users":         self.entity_manager.get_instance_id()})

    @Route("/test2", "post_test", methods=["GET"])
    async def post_test(self):
        entity_manager = EntityManager()

        return self.json({"users":         entity_manager.get_instance_id()})

    @Route("/test3", "put_test", methods=["GET"])
    async def put_test(self):
        Session.flush()

        return self.json({"products": ["Product 1", "Product 2"]})
