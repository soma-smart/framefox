
import json, logging, time
from pathlib import Path
from typing import Dict, Any, Type

from framefox.core.di.service_definition import ServiceDefinition

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceCacheManager:
    """
    Cache manager for ServiceContainer services.
    Separates cache logic from the main container.
    """

    def __init__(self, settings=None):
        self._logger = logging.getLogger("SERVICE_CACHE")
        self.settings = settings
        self._cache_dir = Path("var/cache")
        self._dev_cache_file = self._cache_dir / "dev_services.json"
        self._prod_cache_file = self._cache_dir / "services.json"

    def is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        if not cache_data or "version" not in cache_data:
            return False

        if cache_data.get("version") != "1.0":
            self._logger.debug("Cache version mismatch")
            return False

        if self.settings and hasattr(self.settings, 'app_env'):
            if self.settings.app_env == "dev":
                cache_age = time.time() - cache_data.get('timestamp', 0)
                if cache_age > 300:
                    self._logger.debug("Dev cache expired (5min)")
                    return False

        scan_timestamp = cache_data.get('scan_timestamp', 0)
        if self._are_source_files_modified(scan_timestamp):
            self._logger.debug("Source files modified since cache creation")
            return False

        return True

    def load_cache(self) -> Dict[str, Any]:
        cache_file = self._get_cache_file()
        
        if not cache_file.exists():
            return {}

        try:
            with open(cache_file) as f:
                cache_data = json.load(f)
                
            if self.is_cache_valid(cache_data):
                self._logger.debug(f"Cache loaded successfully from {cache_file.name}")
                return cache_data
            else:
                self._logger.debug("Cache invalid, will rebuild")
                return {}
                
        except Exception as e:
            self._logger.debug(f"Failed to load cache: {e}")
            return {}

    def save_cache(self, cache_data: Dict[str, Any]) -> None:
        cache_file = self._get_cache_file()
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            cache_data['timestamp'] = time.time()
            cache_data['version'] = "1.0"
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            service_count = len(cache_data.get('services', []))
            self._logger.debug(f"Cache saved with {service_count} services to {cache_file.name}")
            
        except Exception as e:
            self._logger.warning(f"Could not save cache: {e}")

    def create_cache_snapshot(self, registry) -> Dict[str, Any]:
        services = []
        
        try:
            all_definitions = registry.get_all_definitions()
            
            for item in all_definitions:
                try:
                    if hasattr(item, 'service_class'):
                        definition = item
                        service_class = definition.service_class
                    elif hasattr(all_definitions, '__getitem__'):
                        service_class = item
                        definition = all_definitions[item]
                    else:
                        self._logger.warning(f"Unknown registry item type: {type(item)}")
                        continue
                    
                    services.append({
                        "name": service_class.__name__,
                        "class_path": f"{service_class.__module__}.{service_class.__name__}",
                        "module": service_class.__module__,
                        "public": getattr(definition, 'public', True),
                        "autowire": getattr(definition, 'autowire', True),
                        "tags": getattr(definition, 'tags', [])
                    })
                    
                except Exception as e:
                    self._logger.debug(f"Failed to process cache item {item}: {e}")
                    continue
            
            return {
                "version": "1.0",
                "timestamp": time.time(),
                "services": services,
                "scan_timestamp": time.time()
            }
            
        except Exception as e:
            self._logger.error(f"Failed to create cache snapshot: {e}")
            return {
                "version": "1.0",
                "timestamp": time.time(),
                "services": [],
                "scan_timestamp": time.time()
            }

    def load_services_from_cache(self, cache_data: Dict[str, Any], registry, scanned_modules: set) -> bool:
        try:
            if "services" not in cache_data:
                return False
            
            loaded_count = 0
            for service_info in cache_data["services"]:
                try:
                    service_class = self._import_service_class(service_info["class_path"])
                    
                    definition = ServiceDefinition(
                        service_class,
                        public=service_info.get("public", True),
                        autowire=service_info.get("autowire", True),
                        tags=service_info.get("tags", [])
                    )
                    
                    registry.register_definition(definition)
                    scanned_modules.add(service_info["module"])
                    loaded_count += 1
                    
                except Exception as e:
                    self._logger.debug(f"Failed to load cached service {service_info.get('name', 'unknown')}: {e}")
                    return False
            
            self._logger.debug(f"Loaded {loaded_count} services from cache")
            return True
            
        except Exception as e:
            self._logger.debug(f"Failed to load services from cache: {e}")
            return False

    def clear_cache(self) -> None:
        try:
            for cache_file in [self._dev_cache_file, self._prod_cache_file]:
                if cache_file.exists():
                    cache_file.unlink()
            self._logger.debug("Cache cleared")
        except Exception as e:
            self._logger.warning(f"Failed to clear cache: {e}")

    def _get_cache_file(self) -> Path:
        if self.settings and hasattr(self.settings, 'app_env') and self.settings.app_env == "dev":
            return self._dev_cache_file
        return self._prod_cache_file

    def _are_source_files_modified(self, cache_timestamp: float) -> bool:
        try:
            src_path = Path("src/controllers")
            if src_path.exists():
                for py_file in src_path.rglob("*.py"):
                    if py_file.stat().st_mtime > cache_timestamp:
                        return True
            
            core_path = Path(__file__).parent.parent
            critical_files = [
                "controller/abstract_controller.py",
                "routing/router.py", 
                "di/service_container.py"
            ]
            
            for critical_file in critical_files:
                file_path = core_path / critical_file
                if file_path.exists() and file_path.stat().st_mtime > cache_timestamp:
                    return True
                    
            return False
        except Exception:
            return True

    def _import_service_class(self, service_path: str) -> Type[Any]:
        import importlib
        
        parts = service_path.split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        module = importlib.import_module(module_path)
        return getattr(module, class_name)
