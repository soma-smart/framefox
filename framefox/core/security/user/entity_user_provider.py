import importlib
import logging
from typing import Any, Optional, Tuple

from framefox.core.config.settings import Settings

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class EntityUserProvider:

    def __init__(
        self,
    ):

        self.settings = Settings()
        self.logger = logging.getLogger("ENTITY_USER_PROVIDER")

    def get_repository_and_property(
        self, firewall_name: str
    ) -> Optional[Tuple[Any, str]]:
        """
        Retrieves the repository and property name for a given firewall.

        Args:
            firewall_name (str): The name of the firewall.

        Returns:
            Optional[Tuple[Any, str]]: A tuple containing the repository and property name or None.
        """
        firewalls = self.settings.firewalls
        firewall_config = firewalls.get(firewall_name, {})
        provider_name = firewall_config.get("provider")
        if not provider_name:
            return None

        provider_config = self.settings.providers.get(provider_name, {})
        entity_class_path = provider_config.get("entity", {}).get("class")
        property_name = provider_config.get("entity", {}).get("property")
        if not entity_class_path or not property_name:
            self.logger.error(
                f"Incomplete configuration for provider '{
                    provider_name}'."
            )
            return None

        try:
            module_path, class_name = entity_class_path.rsplit(".", 1)
            repository_module_path = (
                module_path.replace(".entity.", ".repository.") + "_repository"
            )
            repository_class_name = f"{class_name}Repository"
            module = importlib.import_module(repository_module_path)
            repository_class = getattr(module, repository_class_name)
            repository_instance = repository_class()
            return repository_instance, property_name
        except (ImportError, AttributeError) as e:
            self.logger.error(
                f"Error loading repository for entity '{
                    entity_class_path}': {e}"
            )
            return None
