from fastapi import Request, Response

from framefox.core.debug.profiler.collector.data_collector import DataCollector


class RouteDataCollector(DataCollector):
    def __init__(self):
        super().__init__("route", "fa-map-signs")

    def collect(self, request: Request, response: Response) -> None:
        from framefox.core.routing.router import Router

        endpoint = request.scope.get("endpoint", None)
        path = request.url.path
        route_name = "unknown"
        controller_name = "unknown"
        method_name = "unknown"
        allowed_methods = []
        template = None

        if endpoint:
            full_name = getattr(endpoint, "__qualname__", str(endpoint))
            if "." in full_name:
                parts = full_name.split(".", 1)
                controller_name = parts[0]
                method_name = parts[1]
            else:
                method_name = full_name

            module_name = getattr(endpoint, "__module__", "")
            if module_name and controller_name != "unknown":
                controller_name = f"{module_name}.{controller_name}"

            if hasattr(endpoint, "route_info"):
                route_info = getattr(endpoint, "route_info")
                if isinstance(route_info, dict) and "methods" in route_info:
                    allowed_methods = route_info.get("methods", [])

            for name, route_path in Router._routes.items():
                route_parts = route_path.split("/")
                path_parts = path.split("/")

                if len(route_parts) == len(path_parts):
                    match = True
                    for i, (route_part, path_part) in enumerate(
                        zip(route_parts, path_parts)
                    ):
                        if (
                            route_part
                            and route_part[0] == "{"
                            and route_part[-1] == "}"
                        ):
                            continue
                        if route_part != path_part:
                            match = False
                            break

                    if match:
                        route_name = name
                        break
            if hasattr(response, "template_name"):
                template = response.template_name

            elif hasattr(request.state, "template"):
                template = request.state.template
            elif hasattr(endpoint, "__self__"):
                controller_instance = getattr(endpoint, "__self__")
                if hasattr(controller_instance, "_last_rendered_template"):
                    template = controller_instance._last_rendered_template

        self.data = {
            "route": path,
            "route_name": route_name,
            "endpoint": str(endpoint),
            "controller_name": controller_name,
            "method_name": method_name,
            "allowed_methods": allowed_methods,
            "template": template,
        }
