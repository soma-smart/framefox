import gc

from starlette.middleware.base import BaseHTTPMiddleware
from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class MemoryCleanupMiddleware(BaseHTTPMiddleware):
    """Middleware for periodic memory cleanup."""
    
    def __init__(self, app, cleanup_interval: int = 20):
        super().__init__(app)
        self.request_count = 0
        self.cleanup_interval = cleanup_interval

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        self.request_count += 1
        
        if self.request_count % self.cleanup_interval == 0:
            try:
                container = ServiceContainer()
                container.cleanup_memory()
                
                collected = gc.collect()
                
                if collected > 0:
                    print(f"🧹 Memory cleanup: {collected} objects collected")
                    
            except Exception as e:
                pass
        
        return response
