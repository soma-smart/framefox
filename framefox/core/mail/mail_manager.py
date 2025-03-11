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

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class MailManager:
    """Email management service."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("MAIL")
        self.queue = []
        self.is_processing = False
        self.templates_env = None

        templates_dir = Path(os.getcwd()) / self.settings.mail_templates_dir
        if templates_dir.exists():
            self.templates_env = Environment(
                loader=FileSystemLoader(str(templates_dir))
            )

    async def send_template_email(
        self,
        sender: str,
        receiver: str,
        subject: str,
        template_name: str,
        context: Dict,
        **kwargs,
    ) -> bool:
        """
        Sends an email using a template.

        Args:
            sender: Sender's email address
            receiver: Email recipient (single address)
            subject: Email subject
            template_name: Template file name (without extension)
            context: Data to pass to the template
            **kwargs: Other options for EmailMessage

        Returns:
            True if the email was successfully sent or queued
        """
        if not self.templates_env:
            self.logger.error(
                f"Template folder not found: {self.settings.mail_templates_dir}"
            )
            return False

        try:
            html_template = self.templates_env.get_template(
                f"{template_name}.html.jinja2"
            )
            html_content = html_template.render(**context)

            text_content = None
            try:
                text_template = self.templates_env.get_template(
                    f"{template_name}.txt.jinja2"
                )
                text_content = text_template.render(**context)
            except:
                text_content = self._html_to_text(html_content)

            message = EmailMessage(
                sender=sender,
                receiver=receiver,
                subject=subject,
                body=text_content,
                html_body=html_content,
                cc=kwargs.get("cc", []),
                bcc=kwargs.get("bcc", []),
                priority=kwargs.get("priority", 1),
            )

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
                f"Error sending template email '{template_name}': {str(e)}"
            )
            return False

    async def _send_email_now(self, message: EmailMessage) -> bool:
        """
        Sends an email immediately.

        Args:
            message: The email to send

        Returns:
            True if the email was successfully sent
        """
        mail_config = self.settings.mail_config

        if not self._validate_config():
            self.logger.error("Invalid or incomplete SMTP configuration")
            return False

        if not message.sender:
            self.logger.error(
                "No sender address defined for this email"
            )
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = message.sender
        msg["To"] = message.receiver

        if message.cc:
            msg["Cc"] = ", ".join(message.cc)
        if message.bcc:
            msg["Bcc"] = ", ".join(message.bcc)

        msg.attach(MIMEText(message.body, "plain"))
        if message.html_body:
            msg.attach(MIMEText(message.html_body, "html"))

        for attachment in message.attachments:
            filepath = attachment["filepath"]
            filename = attachment["filename"]

            try:
                with open(filepath, "rb") as file:
                    part = MIMEApplication(file.read(), Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    msg.attach(part)
            except Exception as e:
                self.logger.error(
                    f"Error adding attachment {filepath}: {str(e)}"
                )

        try:
            all_receivers = [message.receiver]
            all_receivers.extend(message.cc)
            all_receivers.extend(message.bcc)

            await aiosmtplib.send(
                message=msg,
                hostname=mail_config["host"],
                port=mail_config["port"],
                username=mail_config["username"],
                password=mail_config["password"],
                use_tls=mail_config["use_tls"],
                validate_certs=self.settings.app_env == "prod",
                recipient_addresses=all_receivers,
                sender=msg["From"],
            )

            self.logger.info(
                f"Email sent: {message.subject} to {message.receiver}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
