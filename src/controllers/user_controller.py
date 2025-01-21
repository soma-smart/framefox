from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from typing import Optional, Dict
from src.repository.user_repository import UserRepository
from src.entity.user import User
from framefox.core.orm.entity_manager import EntityManager


class UserController(AbstractController):
    def __init__(self, entityManager: EntityManager):
        self.entity_manager = entityManager

    @Route("/user", "read_all", methods=["GET"])
    async def read_all(self):
        return UserRepository().find_all()

    @Route("/user/{id}", "read", methods=["GET"])
    async def read(self, id: int):
        return UserRepository().find({"id": id})

    @Route("/user", "create", methods=["POST"])
    async def create(self, user: User.generate_create_model()):
        entity_instance = UserRepository().model(**user.dict())
        self.entity_manager.persist(entity_instance)
        self.entity_manager.commit()
        return self.json(
            data={"message": "Created successfully",
                  "id": entity_instance.id},
            status=201
        )

    @Route("/user", "update", methods=["PUT"])
    async def update(self, user: User):
        self.entity_manager.persist(user)
        self.entity_manager.commit()
        return self.json(
            data={"message": "Updated successfully"},
            status=200
        )

    @Route("/user/{id}", "delete", methods=["DELETE"])
    async def delete(self, id: int):
        entity_instance = UserRepository().find(id)
        self.entity_manager.delete(entity_instance)
        self.entity_manager.commit()
        return self.json(
            data={"message": "Deletion success"},
            status=204
        )
