<<<<<<< Updated upstream
<<<<<<< Updated upstream
from src.core.routing.decorator.route import Route
from src.repository.user_repository import UserRepository
from src.entity.user import User
from src.core.controller.abstract_controller import AbstractController
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
from typing import Optional, Dict

from src.entity.user import User
from src.repository.user_repository import UserRepository

from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController


class UserController(AbstractController):
    """
    Example
    """

    @Route("/users", "get_users", methods=["GET"])
    async def get_users(self):
        return UserRepository().find_all()

    @Route("/users/search", "search_users", methods=["POST"])
    async def search_users(
        self,
        criteria: Dict[str, str],
        order_by: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        users = UserRepository().find_by(criteria, order_by, limit, offset)
        return users

    @Route("/users/find", "get_user", methods=["POST"])
    async def get_user(self, keys_formula: User.generate_find_model()):
        return UserRepository().find(keys_formula.dict())

    @Route("/users", "create_user", methods=["POST"])
    async def create_user(self, user: User):
        user_instance = UserRepository().model(**user.dict())
        self.entity_manager.persist(user_instance)
        self.entity_manager.commit()

    @Route("/users", "update_user", methods=["PUT"])
    async def update_user(self, user: User):
        self.entity_manager.persist(user)
        self.entity_manager.commit()

    @Route("/users/{id}", "delete_user", methods=["DELETE"])
    async def delete_user(self, id: int):
        user_instance = UserRepository().find(id)
        self.entity_manager.delete(user_instance)
        self.entity_manager.commit()
