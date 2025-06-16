from typing import Any, Dict, Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël & BOUMAZA Rayen
Github: https://github.com/Vasulvius & https://github.com/RayenBou
"""


class SessionInterface:
    def __init__(self):
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the session"""
        pass

    def set(self, key: str, value: Any) -> None:
        """Set a value in the session"""
        pass

    def has(self, key: str) -> bool:
        """Check if a key exists in the session"""
        pass

    def remove(self, key: str) -> None:
        """Remove a value from the session"""
        pass

    def clear(self) -> None:
        """Completely clear the session"""
        pass

    def get_id(self) -> Optional[str]:
        """Retrieve the session ID"""
        pass

    def migrate(self, destroy: bool = False) -> bool:
        """
        Migrate the session to a new ID
        If destroy=True, the previous session is deleted
        """
        pass

    def invalidate(self) -> bool:
        """Invalidate the session and generate a new ID"""
        pass

    def get_all(self) -> Dict:
        """Retrieve all session data"""
        pass

    def get_flash_bag(self):
        """Retrieve the flash message manager"""
        pass

    def save(self) -> None:
        """Save the session data"""
        pass
