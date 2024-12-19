from src.core.routing.decorator.route import Route
from src.repository.user_repository import UserRepository
from src.core.controller.abstract_controller import AbstractController
from typing import Optional, Dict


class UserController(AbstractController):
    """
    Example
    """

    def __init__(self):
        super().__init__()

    @Route("/users", "get_users", methods=["GET"])
    async def get_users(self):

        # Session.set("last_visited", "/users")

        # return self.render("users.html", {"title": "user list"})
        return UserRepository().find_all()

    @Route("/users/search", "search_users", methods=["POST"])
    async def search_users(
        self,
        criteria: Dict[str, str],
        order_by: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        users = UserRepository().find_by(
            criteria, order_by, limit, offset)
        return users

    @Route("/users/{id}", "get_user", methods=["GET"])
    async def get_user(self, id: int):
        return UserRepository().find(id)

    @Route("/users", "create_user", methods=["POST"])
    async def create_user(self, user: UserRepository().create_model):
        user_instance = UserRepository().model(**user.dict())
        UserRepository().add(user_instance)
        return None

    @Route("/users/{id}", "update_user", methods=["PUT"])
    async def update_user(self, id: int, user: UserRepository().create_model):
        return UserRepository().update(id, user)

    @Route("/users/{id}", "delete_user", methods=["DELETE"])
    async def delete_user(self, id: int):
        return UserRepository().delete(id)
