

from src.core.controller.abstract_controller import AbstractController


class UserController(AbstractController):
    def __init__(self):
        super().__init__()
        self.add_route("/users", "get_users", self.get_users)
        self.add_route("/users/<int:user_id>", "get_user", self.get_user)
        self.add_route("/vue", "get_vue", self.get_vue)

    def get_users(self):
        return self.jsonify({"users": ["Alice", "Bob"]})

    def get_user(self, user_id):
        return self.jsonify({"user": {"id": user_id, "name": "Alice"}})

    def get_vue(self):
        return self.jsonify({"user": {"id": 1, "name": "Alice"}})
