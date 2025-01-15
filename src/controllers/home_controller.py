from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from fastapi import Request
from framefox.core.request.session.session import Session
from framefox.core.orm.entity_manager import EntityManager
from framefox.core.di.service_container import ServiceContainer
from framefox.core.config.settings import Settings


class HomeController(AbstractController):

    @Route("/", "show_home", methods=["GET"])
    async def show_home(self, request: Request):
        # Récupérer les cookies
        cookies = request.cookies
        service_container = ServiceContainer()
        service_container.print_container_stats()

        # Récupérer la session

        return self.json(
            {
                "message": "Welcome to the home page!",
                "cookies": cookies,
            }
        )
