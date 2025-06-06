from typing import Any, Type
from pydantic import BaseModel
from framefox.core.di.service_factory_manager import ServiceFactory
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""
class PydanticModelFactory(ServiceFactory):
    """
    Factory for creating Pydantic model instances with dependency injection support.
    
    This factory handles the creation of Pydantic models by attempting different
    instantiation strategies, from simple default construction to using type-based
    default values as fallback options.
    """
    
    def supports(self, service_class: Type[Any]) -> bool:
        """Check if this factory can create Pydantic models."""
        try:
            return (
                hasattr(service_class, '__bases__') and 
                any(issubclass(base, BaseModel) for base in service_class.__mro__)
            )
        except:
            return False
    
    def create(self, service_class: Type[Any], container: "ServiceContainer") -> Any:
        """Create a Pydantic model instance with default/empty values."""
        try:
            return service_class()
        except Exception:
            try:
                default_values = self._get_default_values(service_class)
                return service_class(**default_values)
            except Exception:
                return service_class.construct()
    
    def _get_default_values(self, model_class: Type[BaseModel]) -> dict:
        """Generate default values based on field types."""
        defaults = {}
        
        if hasattr(model_class, 'model_fields'):
            for field_name, field_info in model_class.model_fields.items():
                field_type = field_info.annotation
                defaults[field_name] = self._get_default_for_type(field_type)
        
        return defaults
    
    def _get_default_for_type(self, field_type: Type) -> Any:
        """Get a sensible default value for a given type."""
        type_defaults = {
            str: "",
            int: 0,
            float: 0.0,
            bool: False,
            list: [],
            dict: {},
        }
        
        return type_defaults.get(field_type, None)
    
    def get_priority(self) -> int:
        return 100