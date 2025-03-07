from typing import Any, Dict, Optional


class SessionInterface:
    def __init__(self):
        """
        Constructeur avec arguments optionnels pour faciliter l'instanciation.
        Cette méthode ne fait rien car SessionInterface est une interface.
        """
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de la session"""
        pass

    def set(self, key: str, value: Any) -> None:
        """Définit une valeur dans la session"""
        pass

    def has(self, key: str) -> bool:
        """Vérifie si une clé existe dans la session"""
        pass

    def remove(self, key: str) -> None:
        """Supprime une valeur de la session"""
        pass

    def clear(self) -> None:
        """Vide complètement la session"""
        pass

    def get_id(self) -> Optional[str]:
        """Récupère l'ID de la session"""
        pass

    def migrate(self, destroy: bool = False) -> bool:
        """
        Migre la session vers un nouvel ID
        Si destroy=True, la session précédente est supprimée
        """
        pass

    def invalidate(self) -> bool:
        """Invalide la session et génère un nouvel ID"""
        pass

    def get_all(self) -> Dict:
        """Récupère toutes les données de la session"""
        pass

    def get_flash_bag(self):
        """Récupère le gestionnaire de messages flash"""
        pass
