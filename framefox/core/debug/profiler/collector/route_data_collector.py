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

            if hasattr(endpoint, "__original_method__"):

                original_method = endpoint.__original_method__
                controller_name = getattr(endpoint, "__controller_name__", "unknown")
                method_name = getattr(endpoint, "__method_name__", "unknown")

                if hasattr(original_method, "__qualname__"):
                    module_name = getattr(original_method, "__module__", "")
                    if module_name and "." in module_name:

                        module_parts = module_name.split(".")
                        if len(module_parts) >= 3:
                            controller_file = module_parts[-1]
                            if controller_file.endswith("_controller"):
                                controller_name = controller_file.replace("_controller", "").title() + "Controller"

                if hasattr(endpoint, "route_info") and isinstance(endpoint.route_info, dict):
                    allowed_methods = endpoint.route_info.get("methods", [])
                elif hasattr(original_method, "route_info") and isinstance(original_method.route_info, dict):
                    allowed_methods = original_method.route_info.get("methods", [])
            else:
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
                    for i, (route_part, path_part) in enumerate(zip(route_parts, path_parts)):
                        if route_part and route_part[0] == "{" and route_part[-1] == "}":
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
            elif hasattr(request.state, "controller_instance"):
                controller_instance = request.state.controller_instance
                if hasattr(controller_instance, "_last_rendered_template"):
                    template = controller_instance._last_rendered_template
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
