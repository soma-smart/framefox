from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.security.password.password_hasher import PasswordHasher
from src.entity.user import User
from src.repository.user_repository import UserRepository
from fastapi import Request


class RegisterController(AbstractController):

    @Route("/register", "register_user", methods=["GET", "POST"])
    async def register_user(self, request: Request):
        user = User()

        if request.method == "POST":
            form = await request.form()
            user = User()
            user.email = form.get("email")
            user.password = PasswordHasher().hash_password(form.get("password"))

            self.entity_manager.persist(user)
            self.entity_manager.commit()
            return self.redirect("/login")

        return self.render("register.html")
