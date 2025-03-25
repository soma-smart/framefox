from fastapi import Request
from framefox.core.orm.entity_manager import EntityManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
---------------------------- 
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class EntityManagerMiddleware:
    """Middleware that manages the lifecycle of sessions for each request"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        entity_manager = EntityManager()

        request = Request(scope)
        request.state.entity_manager = entity_manager

        try:
            response = None

            async def wrapped_send(message):
                nonlocal response
                if message["type"] == "http.response.start":
                    response = message
                await send(message)

            await self.app(scope, receive, wrapped_send)

            if response and 200 <= response.get("status", 500) < 300:
                entity_manager.commit()
        except Exception as e:

            entity_manager.rollback()
            raise
        finally:
            entity_manager.close_session()
