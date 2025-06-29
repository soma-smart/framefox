from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from src.repository.user_repository import UserRepository
from src.security.auth import hash_password, verify_password
from framefox.core.http.request import Request
from framefox.core.http.response import ResponseRedirect
from sqlalchemy.ext.asyncio import AsyncSession
from framefox.dependencies import get_async_session

class AuthController(AbstractController):
    def __init__(self):
        super().__init__()
        self.user_repository = None

    async def init_repos(self, session: AsyncSession):
        self.user_repository = UserRepository(session)

    @Route("/auth/register", "auth.register", methods=["GET", "POST"])
    async def register(self, request: Request):
        session: AsyncSession = await get_async_session()

        await self.init_repos(session)
        if request.method == "POST":
            form = await request.form()
            username = form.get("username")
            email = form.get("email")
            password = form.get("password")
            existing_user = await self.user_repository.find_by_username(username)
            if existing_user:
                return self.render("security/register.html", {"error": "Username already taken"})

            hashed = hash_password(password)

            await self.user_repository.create_user(username, email, hashed)
            return ResponseRedirect("/auth/login")

        return self.render("security/register.html")

    @Route("/auth/login", "auth.login", methods=["GET", "POST"])
    async def login(self, request: Request):
        session: AsyncSession = await get_async_session()

        await self.init_repos(session)
        if request.method == "POST":
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
            user = await self.user_repository.find_by_username(username)
            if not user or not verify_password(password, user.password_hash):
                return self.render("security/login.html", {"error": "Invalid credentials"})

            request.session["user_id"] = user.id

            return ResponseRedirect("/")

        return self.render("security/login.html")

    @Route("/auth/logout", "auth.logout", methods=["GET"])
    async def logout(self, request: Request):
        request.session.pop("user_id", None)

        return ResponseRedirect("/auth/login")
