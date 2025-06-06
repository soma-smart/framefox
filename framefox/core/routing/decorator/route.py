import inspect
from functools import wraps
from typing import get_type_hints

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Route:
    """
    A decorator class to define route information for a web framework with dependency injection support.
    """

    def __init__(self, path: str, name: str, methods: list, response_model=None):
        self.path = path
        self.name = name
        self.methods = methods
        self.response_model = response_model

    def __call__(self, func):
        original_sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
         
            controller_instance = args[0] if args else None
            
            if controller_instance and hasattr(controller_instance, '_container'):
             
                for param_name, param in original_sig.parameters.items():
                    if param_name == 'self':
                        continue
                    
                    if param_name in kwargs:
                        continue
                    
                   
                    param_type = type_hints.get(param_name)
                    
                    if param_type and param_type != type(None):
                    
                        if self._is_fastapi_native_type(param_type):
                            continue
                        
                        try:
                            service = controller_instance._container.get(param_type)
                            kwargs[param_name] = service
                        except Exception as e:
                    
                            if param.default != inspect.Parameter.empty:
                                kwargs[param_name] = param.default
                            else:
                            
                                import logging
                                logger = logging.getLogger("CONTAINER")
                                logger.error(f"Could not inject {param_type.__name__} for {func.__name__}.{param_name}: {e}")
                                raise RuntimeError(f"Dependency injection failed for {param_type.__name__}")
            
            return await func(*args, **kwargs)

        self._create_fastapi_signature(wrapper, original_sig, type_hints)
        

        wrapper.route_info = {
            "path": self.path,
            "name": self.name,
            "methods": self.methods,
            "response_model": self.response_model,
            "original_function": func,
        }
        
        return wrapper

    def _create_fastapi_signature(self, wrapper_func, original_sig, type_hints):
        """Create a FastAPI-compatible signature by removing injected dependencies."""
        new_params = []
        
        for param_name, param in original_sig.parameters.items():
            if param_name == 'self':
                new_params.append(param)
                continue
            param_type = type_hints.get(param_name)
  
            if param_type and self._is_fastapi_native_type(param_type):
                new_params.append(param)
                continue

            if not param_type:
                new_params.append(param)
                continue

            if self._is_path_parameter(param_name):
                new_params.append(param)
                continue
                
        wrapper_func.__signature__ = original_sig.replace(parameters=new_params)

    def _is_path_parameter(self, param_name: str) -> bool:
        """Check if parameter is a path parameter (exists in route path)."""
        return f"{{{param_name}}}" in self.path

    def _is_fastapi_native_type(self, param_type) -> bool:
        """Check if the parameter type is a FastAPI native type that shouldn't be injected."""
        fastapi_native_modules = {
            'fastapi', 'starlette'
        }
        
        fastapi_types = {
            'Request', 'Response', 'BackgroundTasks', 'WebSocket',
            'HTTPException', 'Depends', 'Security', 'Cookie', 'Header',
            'Query', 'Path', 'Body', 'Form', 'File', 'UploadFile'
        }
        
        type_name = getattr(param_type, '__name__', str(param_type))
        type_module = getattr(param_type, '__module__', '')

        if type_name in fastapi_types:
            return True
            
        for module in fastapi_native_modules:
            if type_module.startswith(module):
                return True
        
     
        if type_module.startswith('pydantic'):
       
            from pydantic import BaseModel
            if hasattr(param_type, '__bases__') and BaseModel in getattr(param_type, '__mro__', []):
        
                return False
        
            return True
        
        return False
