from functools import wraps

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Route:
    """
    A decorator class to define route information for a web framework.

    Attributes:
        path (str): The URL path for the route.
        name (str): The name of the route.
        methods (list): A list of HTTP methods (e.g., ['GET', 'POST']) that the route responds to.

    Methods:
        __call__(func):
            Wraps the given function to include route information.
            Args:
                func (callable): The function to be wrapped.
            Returns:
                callable: The wrapped function with route information attached.
    """

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
            "methods": self.methods,
        }
        return wrapper
