from src.core.controller.abstract_controller import AbstractController
from fastapi import Request


class UserController(AbstractController):
    def __init__(self):
        super().__init__()
        self.add_route("/users", "get_users", self.get_users, methods=["GET"])
        self.add_route("/users/{user_id}", "get_user",
                       self.get_user, methods=["GET"])

    async def get_users(self, request: Request):
        hello = self.get_query_param("hello")
        return self.render(request, "users.html")

    async def get_user(self, user_id: int):

        return self.json({"user": {"id": user_id, "name": "Alice"}})
