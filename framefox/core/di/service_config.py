from pathlib import Path
from typing import Any, Dict, List

import yaml

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceConfig:
    """Loads and manages service configuration from a YAML file"""

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        config_path = Path("config/services.yaml")
        self.config = self._load_config(config_path)

        self.excluded_dirs = set()
        self.excluded_modules = set()

        self._parse_config()

        self._initialized = True

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Loads the YAML configuration file"""
        if not config_path.exists():
            return {
                "services": {
                    "_defaults": {
                        "autowire": True,
                        "autoconfigure": True,
                        "public": False,
                    }
                }
            }

        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def _parse_config(self) -> None:
        """Parses the configuration and sets global parameters"""
        services_config = self.config.get("services", {})
        defaults = services_config.get("_defaults", {})

        self.autowire_enabled = defaults.get("autowire", True)
        self.autoconfigure_enabled = defaults.get("autoconfigure", True)
        self.default_public = defaults.get("public", False)

        self.excluded_modules = set()
        self.excluded_classes = set()
        self.excluded_dirs = set()

        exclude_config = services_config.get("_exclude", {})

        for module in exclude_config.get("modules", []):
            self.excluded_modules.add(module)

        for class_name in exclude_config.get("classes", []):
            self.excluded_classes.add(class_name)

        for directory in exclude_config.get("directories", []):
            self.excluded_dirs.add(directory)

        for key, value in services_config.items():
            if key.endswith("\\"):
                if "exclude" in value:
                    excludes = value["exclude"]
                    if isinstance(excludes, str):
                        self._parse_exclude_pattern(excludes)
                    elif isinstance(excludes, list):
                        for exclude in excludes:
                            self._parse_exclude_pattern(exclude)

    def is_excluded_module(self, module_name: str) -> bool:
        """Checks if a module should be excluded"""
        return any(module_name == excluded or module_name.startswith(f"{excluded}.") for excluded in self.excluded_modules)

    def is_excluded_class(self, class_name: str) -> bool:
        """Checks if a class should be excluded based on its name"""
        return class_name in self.excluded_classes

    def is_in_excluded_directory(self, module_path: str) -> bool:
        """Checks if a module is in an excluded directory"""
        parts = module_path.split(".")
        return any(excluded in parts for excluded in self.excluded_dirs)

    def _parse_exclude_pattern(self, pattern: str) -> None:
        """Parses exclusion patterns and adds them to the appropriate lists"""
        if pattern.startswith("../"):
            path = pattern.strip("{}").replace("{", "").replace("}", "")
            dirs = [d.strip() for d in path.split(",")]
            for dir in dirs:
                if dir.startswith("../"):
                    dir = dir[3:]
                self.excluded_dirs.add(dir)
        else:
            self.excluded_modules.add(pattern)

    def is_public(self, service_class) -> bool:
        """Determines if a service should be public"""
        service_name = f"{service_class.__module__}.{service_class.__name__}".lower().replace(".", "\\")
        for pattern, config in self.config.get("services", {}).items():
            if pattern != "_defaults" and not pattern.endswith("\\"):
                if pattern.lower() == service_name:
                    return config.get("public", self.default_public)

        return self.default_public

    def get_service_tags(self, service_class) -> List[str]:
        """Returns the tags configured for a specific service"""
        service_name = f"{service_class.__module__}.{service_class.__name__}".lower().replace(".", "\\")
        tags = []
        if self.autoconfigure_enabled:
            for base in service_class.__mro__:
                if base.__name__.startswith("I") and not base.__name__ == "Interface":
                    tags.append(f"interface.{base.__name__[1:].lower()}")

        for pattern, config in self.config.get("services", {}).items():
            if pattern != "_defaults" and not pattern.endswith("\\"):
                if pattern.lower() == service_name and "tags" in config:
                    if isinstance(config["tags"], list):
                        tags.extend(config["tags"])
                    else:
                        tags.append(config["tags"])

        return tags
