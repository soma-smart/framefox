from typing import Any, Dict, List


class FlashBagInterface:

    def add(self, type: str, message: Any) -> None:
        """Ajoute un message flash"""
        pass

    def peek(self, type: str, default: Any = None) -> List:
        """Récupère les messages sans les supprimer"""
        pass

    def get(self, type: str, default: Any = None) -> List:
        """Récupère les messages et les supprime"""
        pass

    def set_all(self, messages: Dict[str, List]) -> None:
        """Remplace tous les messages flash"""
        pass

    def get_all(self) -> Dict[str, List]:
        """Récupère tous les messages et les supprime"""
        pass

    def has(self, type: str) -> bool:
        """Vérifie si des messages du type existent"""
        pass

    def keys(self) -> List[str]:
        """Liste tous les types de messages disponibles"""
        pass
