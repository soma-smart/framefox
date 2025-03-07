import uuid
from typing import Any, Dict, Optional

from fastapi import Request

from framefox.core.request.request_stack import RequestStack
from framefox.core.request.session.flash_bag import FlashBag
from framefox.core.request.session.session_interface import SessionInterface


class Session(SessionInterface):

    def __init__(self):
        self._flash_bag = FlashBag()

    def get_request(self) -> Request:
        """Récupère la requête courante via le RequestStack"""
        return RequestStack.get_request()

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de la session"""
        request = self.get_request()
        return request.state.session_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Définit une valeur dans la session"""
        request = self.get_request()
        if not hasattr(request.state, "session_data"):
            request.state.session_data = {}

        if not hasattr(request.state, "session_id") or not request.state.session_id:
            request.state.session_id = str(uuid.uuid4())

        request.state.session_data[key] = value

    def has(self, key: str) -> bool:
        """Vérifie si une clé existe dans la session"""
        request = self.get_request()
        if not hasattr(request.state, "session_data"):
            return False
        return key in request.state.session_data

    def remove(self, key: str) -> None:
        """Supprime une valeur de la session"""
        request = self.get_request()
        if hasattr(request.state, "session_data") and key in request.state.session_data:
            del request.state.session_data[key]

    def clear(self) -> None:
        """Vide complètement la session"""
        request = self.get_request()
        if hasattr(request.state, "session_data"):
            request.state.session_data.clear()

    def get_id(self) -> Optional[str]:
        """Récupère l'ID de la session"""
        request = self.get_request()
        return getattr(request.state, "session_id", None)

    def migrate(self, destroy: bool = False) -> bool:
        """Migre la session vers un nouvel ID"""
        request = self.get_request()
        old_id = getattr(request.state, "session_id", None)

        # Générer un nouvel ID
        new_id = str(uuid.uuid4())
        request.state.session_id = new_id

        # TODO: Si destroy=True et qu'un SessionManager est disponible,
        # supprimer l'ancienne session

        return True

    def invalidate(self) -> bool:
        """Invalide la session et génère un nouvel ID"""
        self.clear()
        return self.migrate(True)

    def get_all(self) -> Dict:
        """Récupère toutes les données de la session"""
        request = self.get_request()
        return getattr(request.state, "session_data", {})

    def get_flash_bag(self) -> FlashBag:
        """Récupère le gestionnaire de messages flash"""
        if not self.has("_flash_initialized"):
            self._flash_bag.initialize_from_session(self)
            self.set("_flash_initialized", True)
        return self._flash_bag

    def save(self) -> None:
        """Sauvegarde les données flash dans la session"""
        if self.has("_flash_initialized"):
            self._flash_bag.save_to_session(self)

    # Méthodes statiques de compatibilité pour la transition
    @staticmethod
    def get_static(key, default=None):
        """Version statique de get pour compatibilité"""
        return Session().get(key, default)

    @staticmethod
    def set_static(key, value):
        """Version statique de set pour compatibilité"""
        Session().set(key, value)
