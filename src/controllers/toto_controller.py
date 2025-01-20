from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from typing import Optional, Dict
from src.repository.toto_repository import TotoRepository
from src.entity.toto import Toto
from framefox.core.orm.entity_manager import EntityManager


class TotoController(AbstractController):
    def __init__(self, entityManager: EntityManager):
        self.entity_manager = entityManager

    @Route("/toto", "read_all", methods=["GET"])
    async def read_all(self):
        return TotoRepository().find_all()
        # return self.render("blabla.html", {})

    @Route("/toto/{id}", "read", methods=["GET"])
    async def read(self, id: int):
        return TotoRepository().find({"id": id})

    @Route("/toto", "create", methods=["POST"])
    async def create(self, toto: Toto.generate_create_model()):
        entity_instance = TotoRepository().model(**toto.dict())
        self.entity_manager.persist(entity_instance)
        self.entity_manager.commit()

    @Route("/toto", "update", methods=["PUT"])
    async def update(self, toto: Toto):
        self.entity_manager.persist(toto)
        self.entity_manager.commit()

    @Route("/toto/{id}", "delete", methods=["DELETE"])
    async def delete(self, id: int):
        entity_instance = TotoRepository().find(id)
        self.entity_manager.delete(entity_instance)
        self.entity_manager.commit()
