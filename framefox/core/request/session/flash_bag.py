from typing import Any, Dict, List

from framefox.core.request.session.flash_bag_interface import FlashBagInterface

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FlashBag(FlashBagInterface):
    """
    Implementation of the temporary flash message system.
    """

    def __init__(self):
        self._flashes = {}
        self._storage_key = "_flash_messages"

    def add(self, type: str, message: Any) -> None:
        """Adds a flash message"""
        if type not in self._flashes:
            self._flashes[type] = []
        self._flashes[type].append(message)

    def peek(self, type: str, default: Any = None) -> List:
        """Retrieves messages without deleting them"""
        if type not in self._flashes:
            return default if default is not None else []
        return self._flashes[type]

    def get(self, type: str, default: Any = None) -> List:
        """Retrieves messages and deletes them"""
        if type not in self._flashes:
            return default if default is not None else []
        messages = self._flashes[type]
        del self._flashes[type]
        return messages

    def set_all(self, messages: Dict[str, List]) -> None:
        """Replaces all flash messages"""
        self._flashes = messages

    def get_all(self) -> Dict[str, List]:
        """Retrieves all messages and deletes them"""
        all_flashes = self._flashes
        self._flashes = {}
        return all_flashes

    def has(self, type: str) -> bool:
        """Checks if messages of the type exist"""
        return type in self._flashes and len(self._flashes[type]) > 0

    def keys(self) -> List[str]:
        """Lists all available message types"""
        return list(self._flashes.keys())

    def get_storage_key(self) -> str:
        """Key used to store flashes in the session"""
        return self._storage_key

    def initialize_from_session(self, session) -> None:
        """Loads messages from the session"""
        self._flashes = session.get(self._storage_key, {})

    def save_to_session(self, session) -> None:
        """Saves messages to the session"""
        if self._flashes:
            session.set(self._storage_key, self._flashes)
        else:
            session.remove(self._storage_key)

    def get_for_template(self) -> List[Dict[str, str]]:
        result = []
        flashes = self.get_all()

        for category, messages in flashes.items():
            for message in messages:
                result.append({"category": category, "message": message})

        return result
