from typing import Any, Dict

from fastapi import Request, Response

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class DataCollector:
    def __init__(self, name: str, icon: str):
        self.name = name
        self.icon = icon
        self.data = {}

    def collect(self, request: Request, response: Response) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        return self.data
