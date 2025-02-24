import pytest
from framefox.core.routing.decorator.route import Route


"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestRoute:
    @pytest.fixture
    def route_decorator(self):
        """Fixture for the Route decorator"""
        return Route(
            path="/test",
            name="test_route",
            methods=["GET", "POST"]
        )

    @pytest.mark.asyncio
    async def test_route_decorator_attributes(self, route_decorator):
        """Test the attributes of the Route decorator"""
        assert route_decorator.path == "/test"
        assert route_decorator.name == "test_route"
        assert route_decorator.methods == ["GET", "POST"]

    @pytest.mark.asyncio
    async def test_route_decorator_wrapper(self, route_decorator):
        """Test the wrapper of the Route decorator"""
        # Define a test function
        @route_decorator
        async def test_function(param1, param2):
            return f"{param1}-{param2}"

        # Check the route information
        assert hasattr(test_function, "route_info")
        assert test_function.route_info["path"] == "/test"
        assert test_function.route_info["name"] == "test_route"
        assert test_function.route_info["methods"] == ["GET", "POST"]

        # Verify that the function still works
        result = await test_function("hello", "world")
        assert result == "hello-world"

    @pytest.mark.asyncio
    async def test_multiple_routes(self):
        """Test multiple Route decorators"""
        route1 = Route("/path1", "route1", ["GET"])
        route2 = Route("/path2", "route2", ["POST"])

        @route1
        async def function1():
            return "function1"

        @route2
        async def function2():
            return "function2"

        # Check distinct route information
        assert function1.route_info["path"] == "/path1"
        assert function1.route_info["name"] == "route1"
        assert function1.route_info["methods"] == ["GET"]

        assert function2.route_info["path"] == "/path2"
        assert function2.route_info["name"] == "route2"
        assert function2.route_info["methods"] == ["POST"]

        # Verify function execution
        assert await function1() == "function1"
        assert await function2() == "function2"

    @pytest.mark.asyncio
    async def test_route_with_custom_methods(self):
        """Test the Route decorator with custom HTTP methods"""
        custom_methods = ["PUT", "DELETE", "PATCH"]
        route = Route("/custom", "custom_route", custom_methods)

        @route
        async def custom_function():
            return "custom"

        assert custom_function.route_info["methods"] == custom_methods
        assert await custom_function() == "custom"

    @pytest.mark.asyncio
    async def test_route_preserves_docstring(self, route_decorator):
        """Test that the decorator preserves the function's docstring"""
        @route_decorator
        async def documented_function():
            """This function has a docstring"""
            return "test"

        assert documented_function.__doc__ == "This function has a docstring"
        assert await documented_function() == "test"
