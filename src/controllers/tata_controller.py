from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from typing import Optional, Dict
from src.repository.tata_repository import TataRepository
from src.entity.tata import Tata
from framefox.core.orm.entity_manager import EntityManager

from fastapi.responses import JSONResponse


class TataController(AbstractController):
    def __init__(self, entityManager: EntityManager):
        self.entity_manager = entityManager

    @Route("/tata", "read_all", methods=["GET"])
    async def read_all(self):
        return TataRepository().find_all()

    @Route("/tata/{id}", "read", methods=["GET"])
    async def read(self, id: int):
        return TataRepository().find({"id": id})

    @Route("/tata", "create", methods=["POST"])
    async def create(self, tata: Tata.generate_create_model()):
        entity_instance = TataRepository().model(**tata.dict())
        self.entity_manager.persist(entity_instance)
        self.entity_manager.commit()
        return self.json(
            data={"message": "Created successfully",
                  "id": entity_instance.id},
            status=201
        )

    @Route("/tata", "update", methods=["PUT"])
    async def update(self, tata: Tata):
        self.entity_manager.persist(tata)
        self.entity_manager.commit()

    @Route("/tata/{id}", "delete", methods=["DELETE"])
    async def delete(self, id: int):
        entity_instance = TataRepository().find(id)
        self.entity_manager.delete(entity_instance)
        self.entity_manager.commit()
