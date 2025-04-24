from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.command_registry import CommandRegistry

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AbstractBundle(ABC):
    """
    Abstract class that all bundles must implement.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the bundle"""
        pass

    @property
    def dependencies(self) -> List[str]:
        """List of bundles this bundle depends on"""
        return []

    def register_services(self, container: ServiceContainer) -> None:
        """Registers the bundle's services in the container"""
        pass

    def register_commands(self, registry: CommandRegistry) -> None:
        """Registers the bundle's commands in the registry"""
        pass
        
    def get_config_schema(self) -> Dict[str, Any]:
        """Defines the configuration schema of the bundle"""
        return {}
        
    def boot(self, container: ServiceContainer) -> None:
        """Executed after all bundles have been registered"""
        pass
        
    def get_templates_dir(self) -> Optional[str]:
        """Directory containing the bundle's templates"""
        return None
        
    def get_static_dir(self) -> Optional[str]:
        """Directory containing the bundle's static files"""
        return None