import inspect
import logging
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
                    if param_name == 'self' or param_name in kwargs:
                        continue
                    
                    param_type = type_hints.get(param_name)
                    
                    if param_type and param_type != type(None):

                        if (self._is_fastapi_native_type(param_type) or 
                            self._is_pydantic_model(param_type) or
                            self._is_primitive_type(param_type) or
                            self._is_path_parameter(param_name)):
                            continue
                        
                        try:
                            service = controller_instance._container.get(param_type)
                            kwargs[param_name] = service
                        except Exception as e:
                            if param.default != inspect.Parameter.empty:
                                kwargs[param_name] = param.default
                            else:
                                logger = logging.getLogger("ROUTE")
                                logger.error(f"Dependency injection failed for {param_type.__name__} in {func.__name__}.{param_name}: {e}")
                                raise RuntimeError(f"Dependency injection failed for {param_type.__name__}")
            
            return await func(*args, **kwargs)

        self._create_fastapi_signature(wrapper, original_sig, type_hints)
        
        wrapper.route_info = {
            "path": self.path,
            "name": self.name,
            "methods": self.methods,
            "response_model": self.response_model,
            "operation_ids": self._generate_operation_ids(func),
            "original_function": func,
        }
        
        return wrapper

    def _create_fastapi_signature(self, wrapper_func, original_sig, type_hints):
        new_params = []
        
        for param_name, param in original_sig.parameters.items():
            if param_name == 'self':
                new_params.append(param)
                continue
                
            param_type = type_hints.get(param_name)
            
            if self._is_path_parameter(param_name):
                new_params.append(param)
                continue
            

            if param_type and self._is_fastapi_native_type(param_type):
                new_params.append(param)
                continue
            
            if param_type and self._is_pydantic_model(param_type):
                new_params.append(param)
                continue

            if param_type and self._is_primitive_type(param_type):
                new_params.append(param)
                continue

            if not param_type:
                new_params.append(param)
                continue
                
        wrapper_func.__signature__ = original_sig.replace(parameters=new_params)

    def _is_path_parameter(self, param_name: str) -> bool:
        return f"{{{param_name}}}" in self.path

    def _is_pydantic_model(self, param_type) -> bool:
        """Check if the parameter type is a Pydantic model (static or dynamic)."""
        try:
            from pydantic import BaseModel

            if (inspect.isclass(param_type) and 
                hasattr(param_type, '__bases__') and 
                BaseModel in getattr(param_type, '__mro__', [])):
                return True

            if hasattr(param_type, '__pydantic_model__'):
                return True

            type_module = getattr(param_type, '__module__', '')
            if 'pydantic' in type_module and hasattr(param_type, '__fields__'):
                return True
                
            return False
        except Exception:
            return False

    def _is_primitive_type(self, param_type) -> bool:
        """Check if the parameter type is a primitive type."""
        primitive_types = {int, str, float, bool, bytes}
        
        # Basic primitive types
        if param_type in primitive_types:
            return True
        
        # Optional types (Union[type, None])
        if hasattr(param_type, '__origin__'):
            if param_type.__origin__ is type(None):
                return True
            # Union types (Optional[int] = Union[int, None])
            if hasattr(param_type, '__args__'):
                args = getattr(param_type, '__args__', ())
                if len(args) == 2 and type(None) in args:
                    other_type = args[0] if args[1] is type(None) else args[1]
                    return other_type in primitive_types
        
        return False

    def _is_fastapi_native_type(self, param_type) -> bool:
        """Check if the parameter type is a FastAPI native type."""
        fastapi_native_modules = {'fastapi', 'starlette'}
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
        
        return False

    def _generate_operation_ids(self, func) -> dict:
        operation_ids = {}
        path_clean = self.path.replace("/", "_").replace("{", "").replace("}", "").strip("_")
        func_name = func.__name__
        
        for method in self.methods:
            if path_clean:
                operation_id = f"{path_clean}_{func_name}_{method.lower()}"
            else:
                operation_id = f"{func_name}_{method.lower()}"
            
            operation_id = operation_id.replace("-", "_").replace(".", "_")
            operation_ids[method] = operation_id
        
        return operation_ids