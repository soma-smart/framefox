import asyncio
import logging
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from framefox.core.config.settings import Settings
from framefox.core.mail.email_message import EmailMessage


class MailManager:
    """Service de gestion des emails."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("MAIL")
        self.queue = []
        self.is_processing = False
        self.templates_env = None

        # Initialiser l'environnement de templates si le dossier existe
        templates_dir = Path(os.getcwd()) / self.settings.mail_templates_dir
        if templates_dir.exists():
            self.templates_env = Environment(
                loader=FileSystemLoader(str(templates_dir))
            )

    async def send_template_email(
        self,
        sender: str,
        receiver: str,  # Changé en singulier
        subject: str,
        template_name: str,
        context: Dict,
        **kwargs
    ) -> bool:
        """
        Envoie un email en utilisant un template.

        Args:
            sender: Adresse email de l'expéditeur
            receiver: Destinataire de l'email (adresse unique)
            subject: Sujet de l'email
            template_name: Nom du fichier template (sans extension)
            context: Données à passer au template
            **kwargs: Autres options pour EmailMessage

        Returns:
            True si l'email a été envoyé ou mis en file d'attente avec succès
        """
        if not self.templates_env:
            self.logger.error(
                f"Dossier de templates introuvable: {self.settings.mail_templates_dir}")
            return False

        try:
            # Charger les templates HTML et texte si disponibles
            html_template = self.templates_env.get_template(
                f"{template_name}.html.jinja2")
            html_content = html_template.render(**context)

            # Template texte est optionnel
            text_content = None
            try:
                text_template = self.templates_env.get_template(
                    f"{template_name}.txt.jinja2")
                text_content = text_template.render(**context)
            except:
                # Générer une version texte basique depuis HTML
                text_content = self._html_to_text(html_content)

            message = EmailMessage(
                sender=sender,
                receiver=receiver,  # Un seul destinataire
                subject=subject,
                body=text_content,
                html_body=html_content,
                cc=kwargs.get("cc", []),
                bcc=kwargs.get("bcc", []),
                priority=kwargs.get("priority", 1)
            )

            # Ajouter les pièces jointes si spécifiées
            attachments = kwargs.get("attachments", [])
            for att in attachments:
                if isinstance(att, dict):
                    message.add_attachment(
                        att["filepath"], att.get("filename"))
                else:
                    message.add_attachment(att)

            return await self.send_email(message, queue=kwargs.get("queue"))

        except Exception as e:
            self.logger.error(
                f"Erreur lors de l'envoi de l'email template '{template_name}': {str(e)}")
            return False

    # Mettre à jour la méthode _send_email_now

    async def _send_email_now(self, message: EmailMessage) -> bool:
        """
        Envoie un email immédiatement.

        Args:
            message: L'email à envoyer

        Returns:
            True si l'email a été envoyé avec succès
        """
        mail_config = self.settings.mail_config

        if not self._validate_config():
            self.logger.error("Configuration SMTP invalide ou incomplète")
            return False

        # Vérifier si l'adresse sender est spécifiée
        if not message.sender:
            self.logger.error(
                "Aucune adresse d'expédition (sender) n'est définie pour cet email")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = message.subject
        msg['From'] = message.sender
        # Un seul destinataire, pas besoin de join
        msg['To'] = message.receiver

        if message.cc:
            msg['Cc'] = ", ".join(message.cc)
        if message.bcc:
            msg['Bcc'] = ", ".join(message.bcc)

        # Ajouter le corps de l'email (texte et html)
        msg.attach(MIMEText(message.body, 'plain'))
        if message.html_body:
            msg.attach(MIMEText(message.html_body, 'html'))

        # Ajouter les pièces jointes
        for attachment in message.attachments:
            filepath = attachment["filepath"]
            filename = attachment["filename"]

            try:
                with open(filepath, "rb") as file:
                    part = MIMEApplication(file.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
            except Exception as e:
                self.logger.error(
                    f"Erreur lors de l'ajout de la pièce jointe {filepath}: {str(e)}")

        try:
            # Construire la liste complète des destinataires (en commençant par le destinataire principal)
            all_receivers = [message.receiver]
            all_receivers.extend(message.cc)
            all_receivers.extend(message.bcc)

            # Utiliser le mail_config pour tous les paramètres SMTP
            await aiosmtplib.send(
                message=msg,
                hostname=mail_config["host"],
                port=mail_config["port"],
                username=mail_config["username"],
                password=mail_config["password"],
                use_tls=mail_config["use_tls"],
                validate_certs=self.settings.app_env == "prod",
                recipient_addresses=all_receivers,
                sender=msg['From']
            )

            self.logger.info(
                f"Email envoyé: {message.subject} à {message.receiver}")
            return True

        except Exception as e:
            self.logger.error(f"Échec d'envoi de l'email: {str(e)}")
            return False
