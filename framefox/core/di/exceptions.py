"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceContainerError(Exception):
    """Base exception for service container errors."""
    pass


class CircularDependencyError(ServiceContainerError):
    """Raised when a circular dependency is detected."""
    
    def __init__(self, service_class, dependency_chain):
        self.service_class = service_class
        self.dependency_chain = dependency_chain
        chain_str = " -> ".join(cls.__name__ for cls in dependency_chain)
        super().__init__(f"Circular dependency detected: {chain_str} -> {service_class.__name__}")


class ServiceNotFoundError(ServiceContainerError):
    """Raised when a requested service cannot be found."""
    
    def __init__(self, service_class):
        self.service_class = service_class
        super().__init__(f"Service '{service_class.__name__ if hasattr(service_class, '__name__') else service_class}' not found")


class ServiceInstantiationError(ServiceContainerError):
    """Raised when a service cannot be instantiated."""
    
    def __init__(self, service_class, original_error):
        self.service_class = service_class
        self.original_error = original_error
        super().__init__(f"Failed to instantiate service '{service_class.__name__}': {original_error}")


class InvalidServiceDefinitionError(ServiceContainerError):
    """Raised when a service definition is invalid."""
    pass