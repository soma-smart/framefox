import inspect
import logging
import uuid
from functools import wraps
from typing import List, Optional

from fastapi import WebSocket as FastAPIWebSocket

from framefox.core.websocket.web_socket_manager import WebSocketManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class WebSocket:
    """
    Decorator class for managing WebSocket routes with optional automatic connection management and handler support.

    Args:
        path (str): The WebSocket route path.
        name (str): The name of the WebSocket route.
        room (Optional[str], optional): The room identifier for grouping connections. Defaults to None.
        auto_manage (bool, optional): Whether to automatically manage WebSocket connections and messages. Defaults to True.
        handlers (Optional[List], optional): List of handler instances for connection, message, and disconnection events. Defaults to None.
    """

    def __init__(
        self,
        path: str,
        name: str,
        room: Optional[str] = None,
        auto_manage: bool = True,
        handlers: Optional[List] = None,
    ):
        self.path = path
        self.name = name
        self.room = room
        self.auto_manage = auto_manage
        self.handlers = handlers or []

    def __call__(self, func):
        self._original_func = func
        original_sig = inspect.signature(func)

        if self.auto_manage:
            decorator_self = self

            @wraps(func)
            async def wrapper(controller_self, websocket: FastAPIWebSocket, **path_params):
                extracted_params = {}
                if path_params:
                    extracted_params.update(path_params)
                else:
                    extracted_params = decorator_self._extract_params_from_url(str(websocket.url.path))
                return await decorator_self._auto_manage_websocket(func, controller_self, websocket, **extracted_params)

            wrapper.__signature__ = self._create_fastapi_signature(original_sig)
            wrapper.__annotations__ = func.__annotations__

        else:

            @wraps(func)
            async def wrapper(controller_self, websocket):
                return await func(controller_self, websocket)

            params = [
                inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),
                inspect.Parameter(
                    "websocket",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=FastAPIWebSocket,
                ),
            ]
            wrapper.__signature__ = inspect.Signature(params)

        wrapper.websocket_info = {
            "path": self.path,
            "name": self.name,
            "auto_manage": self.auto_manage,
            "room": self.room,
            "handlers": self.handlers,
        }

        return wrapper

    def _create_fastapi_signature(self, original_sig):
        new_params = []
        for param_name, param in original_sig.parameters.items():
            if param_name == "self":
                new_params.append(param)
                break
        websocket_param = inspect.Parameter(
            "websocket",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=FastAPIWebSocket,
        )
        new_params.append(websocket_param)
        return inspect.Signature(new_params)

    def _extract_params_from_url(self, url_path: str) -> dict:
        params = {}
        if "/ws/" in url_path:
            parts = url_path.split("/ws/")[-1].split("/")
            path_parts = self.path.replace("/ws/", "").split("/")
            for i, path_part in enumerate(path_parts):
                if path_part.startswith("{") and path_part.endswith("}"):
                    param_name = path_part[1:-1]
                    if i < len(parts):
                        params[param_name] = parts[i]
        return params

    async def _auto_manage_websocket(self, func, controller_instance, websocket, **kwargs):
        if not websocket or not hasattr(websocket, "accept"):
            raise RuntimeError("WebSocket not found - internal error")
        manager = WebSocketManager()
        connection_id = str(uuid.uuid4())
        user_id = kwargs.get("user_id")
        room = kwargs.get("room") or self.room
        try:
            await manager.connect(websocket, connection_id, user_id, room)
            for handler in self.handlers:
                await handler.on_connect(connection_id, user_id, room)
            while True:
                try:
                    data = await websocket.receive_text()
                    for handler in self.handlers:
                        await handler.on_message(connection_id, data)
                except Exception:
                    break
        except Exception as e:
            logging.getLogger("WEBSOCKET").error(f"WebSocket error: {e}")
        finally:
            for handler in self.handlers:
                await handler.on_disconnect(connection_id)
            await manager.disconnect(connection_id)

    def _is_websocket_native_type(self, param_type) -> bool:
        type_name = getattr(param_type, "__name__", str(param_type))
        return type_name in {"WebSocket", "WebSocketDisconnect", "WebSocketState"}

    def _is_fastapi_native_type(self, param_type) -> bool:
        fastapi_types = {"Request", "Response", "BackgroundTasks", "WebSocket"}
        type_name = getattr(param_type, "__name__", str(param_type))
        type_module = getattr(param_type, "__module__", "")
        return type_name in fastapi_types or "fastapi" in type_module or "starlette" in type_module

    def _is_primitive_type(self, param_type) -> bool:
        return param_type in {int, str, float, bool, bytes}
