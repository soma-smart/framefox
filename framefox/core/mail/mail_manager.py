import asyncio, logging, os, re
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiosmtplib
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from framefox.core.config.settings import Settings
from framefox.core.mail.email_message import EmailMessage
from framefox.core.mail.mail_url_parser import MailUrlParser
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class MailManager:
    """
    Email management service for sending emails, supporting templates, attachments, 
    queuing, and retry logic. Integrates with Jinja2 for templated emails and 
    supports both immediate and queued delivery using SMTP.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("MAIL")
        self.queue = []
        self.is_processing = False
        self.templates_env = None
        templates_dir = None

        if (
            "mail" in self.settings.config
            and "templates_dir" in self.settings.config["mail"]
        ):
            templates_dir = self.settings.config["mail"]["templates_dir"]

        else:
            self.logger.warning("Templates folder not found in config['mail']")

        if not templates_dir:
            templates_dir = self.settings.get_param("mail.templates_dir")

        if not templates_dir:
            templates_dir = "templates/emails"

        possible_paths = [
            Path(os.getcwd()) / templates_dir,
            Path(os.getcwd()) / "src" / templates_dir,
            Path(os.getcwd()) / templates_dir.lstrip("/"),
        ]

        template_path_found = False

        for path in possible_paths:
            if path.exists() and path.is_dir():
                self.templates_env = Environment(
                    loader=FileSystemLoader(str(path)),
                    autoescape=select_autoescape(["html", "xml"]),
                    extensions=["jinja2.ext.do"],
                )
                self.templates_env.globals["now"] = datetime.now
                template_path_found = True
                break

        if not template_path_found:
            self.logger.warning(
                f"No templates folder found in tested paths: {possible_paths}"
            )

    def _validate_config(self) -> bool:
        mail_config = getattr(self.settings, "mail_config", None)

        if not mail_config:
            mail_url = None

            if "mail" in self.settings.config and "url" in self.settings.config["mail"]:
                mail_url = self.settings.config["mail"]["url"]
            else:
                mail_url = self.settings.get_param(
                    "mail.url"
                ) or self.settings.get_param("mail_url")

            if mail_url:
                mail_config = MailUrlParser.parse_url(mail_url)
                self.settings.mail_config = mail_config
            else:
                self.logger.error("No mail configuration found")
                return False

        required_params = ["host", "port"]
        for param in required_params:
            if param not in mail_config:
                self.logger.error(f"Missing required mail parameter: {param}")
                return False

        return True

    def _html_to_text(self, html_content: str) -> str:
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator="\n")
            text = re.sub(r"\n\s*\n", "\n\n", text)
            return text.strip()
        except ImportError:
            text = html_content
            text = re.sub(r"<br\s*/?>|<p>|</p>|<div>|</div>|<tr>|</tr>", "\n", text)
            text = re.sub(r"<[^>]*>", "", text)
            text = re.sub(r"\n\s*\n", "\n\n", text)
            return text.strip()

    async def send_mail(
        self,
        sender: str,
        receiver: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Union[str, Dict[str, str]]]] = None,
        queue: bool = False,
    ) -> bool:
        cc = cc or []
        bcc = bcc or []
        attachments = attachments or []

        message = EmailMessage(
            sender=sender,
            receiver=receiver,
            subject=subject,
            body=text_content,
            html_body=html_content,
            cc=cc,
            bcc=bcc,
            priority=1,
        )

        for attachment in attachments:
            if isinstance(attachment, dict):
                message.add_attachment(
                    attachment["filepath"], attachment.get("filename")
                )
            else:
                message.add_attachment(attachment)

        return await self._process_message(message, queue)

    async def send_template_email(
        self,
        sender: str,
        receiver: str,
        subject: str,
        template_name: str,
        context: Dict,
        **kwargs,
    ) -> bool:
        if not self.templates_env:
            self.logger.error(
                "No template available. Check the templates/emails folder"
            )
            return False

        try:
            html_content = None
            text_content = None

            html_extensions = [".html", ".html.jinja2", ".html.twig"]
            for ext in html_extensions:
                try:
                    template = f"{template_name}{ext}"
                    self.logger.debug(f"Attempting to load HTML template: {template}")
                    html_template = self.templates_env.get_template(template)
                    html_content = html_template.render(**context)
                    self.logger.info(f"HTML template successfully loaded: {template}")
                    break
                except Exception as e:
                    self.logger.debug(f"Failed to load template {template}: {str(e)}")

            if not html_content:
                self.logger.error(f"No HTML template found for {template_name}")
                return False

            text_extensions = [".txt", ".txt.jinja2", ".txt.twig"]
            for ext in text_extensions:
                try:
                    template = f"{template_name}{ext}"
                    self.logger.debug(f"Attempting to load text template: {template}")
                    text_template = self.templates_env.get_template(template)
                    text_content = text_template.render(**context)

                    break
                except Exception as e:
                    self.logger.debug(
                        f"Failed to load text template {template}: {str(e)}"
                    )

            if not text_content:
                self.logger.debug(
                    f"Converting HTML content to text for {template_name}"
                )
                text_content = self._html_to_text(html_content)

            return await self.send_mail(
                sender=sender,
                receiver=receiver,
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                cc=kwargs.get("cc", []),
                bcc=kwargs.get("bcc", []),
                attachments=kwargs.get("attachments", []),
                queue=kwargs.get("queue", False),
            )
        except Exception as e:
            self.logger.error(f"Error sending template {template_name}: {str(e)}")
            return False

    async def _process_message(
        self, message: EmailMessage, queue: bool = False
    ) -> bool:
        queue_enabled = False

        if "mail" in self.settings.config and "queue" in self.settings.config["mail"]:
            queue_enabled = self.settings.config["mail"]["queue"].get("enabled", False)
        else:
            queue_enabled = self.settings.get_param("mail.queue.enabled", False)

        if queue or queue_enabled:
            self.queue.append(message)

            if not self.is_processing:
                asyncio.create_task(self._process_queue())

            return True

        return await self._send_email_now(message)

    async def _process_queue(self) -> None:
        if self.is_processing:
            return

        self.is_processing = True

        max_retries = 3
        retry_interval = 300

        if "mail" in self.settings.config and "queue" in self.settings.config["mail"]:
            max_retries = self.settings.config["mail"]["queue"].get("max_retries", 3)
            retry_interval = self.settings.config["mail"]["queue"].get(
                "retry_interval", 300
            )
        else:
            max_retries = self.settings.get_param("mail.queue.max_retries", 3)
            retry_interval = self.settings.get_param("mail.queue.retry_interval", 300)

        try:
            queue_copy = self.queue.copy()
            self.queue = []

            for message in queue_copy:
                try:
                    result = await self._send_email_now(message)
                    if not result:
                        if message.retry_count < max_retries:
                            message.retry_count += 1
                            self.queue.append(message)
                            self.logger.warning(
                                f"Send failed, retry scheduled ({message.retry_count}/{max_retries})"
                                f" for {message.subject} to {message.receiver}"
                            )
                        else:
                            self.logger.error(
                                f"Abandoning send after {max_retries} attempts: {message.subject} to {message.receiver}"
                            )
                except Exception as e:
                    self.logger.error(f"Error processing a queued message: {str(e)}")
                    if message.retry_count < max_retries:
                        message.retry_count += 1
                        self.queue.append(message)
        except Exception as e:
            self.logger.error(f"Error processing the queue: {str(e)}")
        finally:
            self.is_processing = False

            if self.queue:
                self.logger.info(
                    f"{len(self.queue)} emails remain in the queue. Next attempt in {retry_interval}s"
                )
                await asyncio.sleep(retry_interval)
                asyncio.create_task(self._process_queue())

    async def _send_email_now(self, message: EmailMessage) -> bool:
        if not self._validate_config():
            self.logger.error("Invalid mail configuration, unable to send email")
            return False

        mail_config = self.settings.mail_config

        mime_message = MIMEMultipart("alternative")
        mime_message["From"] = message.sender
        mime_message["To"] = message.receiver
        mime_message["Subject"] = message.subject

        if message.cc:
            mime_message["Cc"] = ", ".join(message.cc)
        if message.bcc:
            mime_message["Bcc"] = ", ".join(message.bcc)

        if message.body:
            mime_message.attach(MIMEText(message.body, "plain"))
        if message.html_body:
            mime_message.attach(MIMEText(message.html_body, "html"))

        for attachment in message.attachments:
            try:
                with open(attachment["filepath"], "rb") as file:
                    part = MIMEApplication(file.read())
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={attachment['filename']}",
                    )
                    mime_message.attach(part)
            except Exception as e:
                self.logger.error(
                    f"Error adding attachment {attachment['filepath']}: {str(e)}"
                )

        all_recipients = [message.receiver]
        if message.cc:
            all_recipients.extend(message.cc)
        if message.bcc:
            all_recipients.extend(message.bcc)

        try:
            smtp_client = aiosmtplib.SMTP(
                hostname=mail_config["host"],
                port=mail_config["port"],
                use_tls=mail_config.get("use_tls", False),
                start_tls=mail_config.get("use_tls", False)
                and not mail_config.get("use_ssl", False),
            )

            await smtp_client.connect()

            if mail_config.get("username") and mail_config.get("password"):
                await smtp_client.login(
                    mail_config["username"], mail_config["password"]
                )

            await smtp_client.send_message(mime_message)
            await smtp_client.quit()

            return True

        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
