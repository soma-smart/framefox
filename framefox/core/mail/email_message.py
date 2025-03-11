from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


@dataclass
class EmailMessage:
    """Class representing an email to be sent."""

    sender: str
    receiver: str
    subject: str
    body: str

    html_body: Optional[str] = None
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 1
    retry_count: int = 0

    def add_attachment(self, filepath: str, filename: Optional[str] = None) -> None:
        """Adds an attachment to the email."""
        self.attachments.append(
            {"filepath": filepath,
                "filename": filename or filepath.split("/")[-1]}
        )
