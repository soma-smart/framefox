from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from datetime import datetime


@dataclass
class EmailMessage:
    """Classe représentant un email à envoyer."""

    # Paramètres principaux
    sender: str
    receiver: str  # Changé de receivers (liste) à receiver (chaîne unique)
    subject: str
    body: str

    # Paramètres secondaires
    html_body: Optional[str] = None
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1 = Haute priorité, 3 = Basse priorité
    retry_count: int = 0  # Nombre de tentatives d'envoi

    def add_attachment(self, filepath: str, filename: Optional[str] = None) -> None:
        """Ajoute une pièce jointe à l'email."""
        self.attachments.append(
            {"filepath": filepath,
                "filename": filename or filepath.split("/")[-1]}
        )
