from dataclasses import dataclass
from typing import Any, Dict


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
