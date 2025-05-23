from fastapi.responses import JSONResponse
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.debug.profiler.profiler import Profiler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class ProfilerController(AbstractController):
    """
    Web profiler controller for Framefox.
    Handles request profiling information display.
    """
    
    def __init__(self):
        self.profiler = Profiler()
    @Route("/_profiler", "profiler.index", methods=["GET"])
    async def profiler_index(self, page: int = 1, limit: int = 50):
        profiles = self.profiler.list_profiles(limit=limit, page=page)
        total_count = len(self.profiler.list_profiles(limit=10000))
        
        return self.render("profiler/index.html", {
            "profiles": profiles,
            "page": page,
            "limit": limit,
            "total": total_count,
            "page_count": (total_count + limit - 1) // limit
        })
    @Route("/_profiler/{token}", "profiler.detail", methods=["GET"])
    async def profiler_detail(self, token: str):

        profile = self.profiler.get_profile(token)
        return self.render("profiler/details.html", {
            "token": token,
            "profile": profile
        })
    
    @Route("/_profiler/{token}/{panel}", "profiler.panel", methods=["GET"])
    async def profiler_panel(self, token: str, panel: str):
        profile = self.profiler.get_profile(token)
        panel_data = profile.get(panel, {})
        
        template_context = {
            "token": token,
            "panel": panel,
            "data": panel_data,
            "profile": profile
        }    
        return self.render(f"profiler/panels/{panel}.html", template_context)

    @Route("/_profiler/{token}/json", "profiler.json", methods=["GET"])
    async def profiler_json(self, token: str):
        profile = self.profiler.get_profile(token)
        return JSONResponse(content=profile)