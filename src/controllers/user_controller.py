from src.core.routing.decorator.route import Route
from src.repository.user_repository import UserRepository
from src.core.controller.abstract_controller import AbstractController
from fastapi import Request


class UserController(AbstractController):

    @Route("/users", "get_users", methods=["GET"])
    async def get_users(self, request: Request):

        user_repository = UserRepository().find_all()

        return self.render(request, "users.html", {
            "users": user_repository,
            "title": "Liste des utilisateurs"
        })

    @ Route("/users/{user_id}", "get_user", methods=["GET"])
    async def get_user(self, user_id: int):

        return self.json({"user": {"id": user_id, "name": "Alice"}})
