from dataclasses import dataclass
from typing import Any, Dict

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


@dataclass
class DatabaseConfig:
    driver: str
    host: str
    port: int
    username: str
    password: str
    database: str
    charset: str = "utf8mb4"
    options: Dict[str, Any] = None
