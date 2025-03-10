from typing import Any, Dict, List

from framefox.core.request.session.flash_bag_interface import FlashBagInterface


class FlashBag(FlashBagInterface):
    """
    Implémentation du système de messages flash temporaires.
    """

    def __init__(self):
        self._flashes = {}
        self._storage_key = "_flash_messages"

    def add(self, type: str, message: Any) -> None:
        """Ajoute un message flash"""
        if type not in self._flashes:
            self._flashes[type] = []
        self._flashes[type].append(message)

    def peek(self, type: str, default: Any = None) -> List:
        """Récupère les messages sans les supprimer"""
        if type not in self._flashes:
            return default if default is not None else []
        return self._flashes[type]

    def get(self, type: str, default: Any = None) -> List:
        """Récupère les messages et les supprime"""
        if type not in self._flashes:
            return default if default is not None else []
        messages = self._flashes[type]
        del self._flashes[type]
        return messages

    def set_all(self, messages: Dict[str, List]) -> None:
        """Remplace tous les messages flash"""
        self._flashes = messages

    def get_all(self) -> Dict[str, List]:
        """Récupère tous les messages et les supprime"""
        all_flashes = self._flashes
        self._flashes = {}
        return all_flashes

    def has(self, type: str) -> bool:
        """Vérifie si des messages du type existent"""
        return type in self._flashes and len(self._flashes[type]) > 0

    def keys(self) -> List[str]:
        """Liste tous les types de messages disponibles"""
        return list(self._flashes.keys())

    def get_storage_key(self) -> str:
        """Clé utilisée pour stocker les flashes dans la session"""
        return self._storage_key

    def initialize_from_session(self, session) -> None:
        """Charge les messages depuis la session"""
        self._flashes = session.get(self._storage_key, {})

    def save_to_session(self, session) -> None:
        """Enregistre les messages dans la session"""
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
