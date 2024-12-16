from functools import wraps


class Route:
    def __init__(self, path: str, name: str, methods: list):
        self.path = path
        self.name = name
        self.methods = methods

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        wrapper.route_info = {
            "path": self.path,
            "name": self.name,
            "methods": self.methods
        }
        return wrapper
