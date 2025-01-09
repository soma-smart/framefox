from datetime import datetime, timezone
import json
import os
from typing import Dict, Optional, Annotated
import logging
from injectable import autowired, Autowired
from src.core.config.settings import Settings


class SessionManager:
    """
    Gestionnaire de sessions qui interagit directement avec le fichier de stockage des sessions.
    """

    @autowired
    def __init__(self, settings: Annotated[Settings, Autowired]):
        self.logger = logging.getLogger("SESSION_MANAGER")
        self.settings = settings
        # Créer le répertoire si nécessaire
        session_dir = os.path.dirname(self.settings.session_file_path)
        # Assurez-vous que le répertoire est créé
        os.makedirs(session_dir, exist_ok=True)

    def load_sessions(self) -> Dict:
        """Charge le fichier de sessions"""
        absolute_path = os.path.abspath(self.settings.session_file_path)
        self.logger.info(
            f"Chargement du fichier de session depuis : {absolute_path}")
        if os.path.exists(absolute_path):
            with open(absolute_path, "r") as f:
                return json.load(f)
        return {}

    def save_sessions(self, session_store: Dict) -> None:
        """Sauvegarde le store de sessions"""
        absolute_path = os.path.abspath(self.settings.session_file_path)
        self.logger.info(
            f"Sauvegarde du fichier de session dans : {absolute_path}")
        with open(absolute_path, "w") as f:
            json.dump(session_store, f)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Récupère une session par son ID"""
        sessions = self.load_sessions()
        self.logger.info(f"Récupération de la session: {session_id}")
        return sessions.get(session_id)

    def create_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Crée une nouvelle session"""
        sessions = self.load_sessions()
        sessions[session_id] = {
            "data": data,
            "expires_at": (datetime.now(timezone.utc).timestamp() + max_age)
        }
        self.save_sessions(sessions)
        self.logger.info(f"Session créée: {session_id}")

    def update_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Met à jour une session existante"""
        sessions = self.load_sessions()
        if session_id in sessions:
            sessions[session_id].update({
                "data": data,
                "expires_at": (datetime.now(timezone.utc).timestamp() + max_age)
            })
            self.save_sessions(sessions)
            self.logger.info(f"Session mise à jour: {session_id}")

    def delete_session(self, session_id: str) -> bool:
        """Supprime une session"""
        sessions = self.load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            self.save_sessions(sessions)
            self.logger.info(f"Session supprimée: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self) -> None:
        """Nettoie les sessions expirées"""
        sessions = self.load_sessions()
        current_time = datetime.now(timezone.utc).timestamp()
        expired = [sid for sid, s in sessions.items() if s["expires_at"]
                   < current_time]

        if expired:
            for sid in expired:
                del sessions[sid]
            self.save_sessions(sessions)
            self.logger.info(f"Sessions expirées nettoyées: {len(expired)}")
