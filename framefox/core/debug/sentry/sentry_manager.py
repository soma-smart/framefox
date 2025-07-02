import logging
from typing import Any, Dict, Optional

from framefox.core.config.settings import Settings
from framefox.core.logging.utils.ansi_cleaner import AnsiCleaner

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SentryManager:
    """
    Sentry integration manager for Framefox.

    This class handles optional Sentry integration, providing error tracking
    and performance monitoring when configured.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if SentryManager._initialized:
            return

        self.settings = Settings()
        self.logger = logging.getLogger("SENTRY")
        self.enabled = False
        self.sentry = None

        if self.settings.sentry_enabled:
            self._initialize_sentry()
        else:
            self.logger.debug("Sentry not configured - skipping initialization")

        SentryManager._initialized = True

    def _initialize_sentry(self):
        """Initialize Sentry if configuration is available"""
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration

            logging_integration = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            )

            # Prepare integrations list
            integrations = [
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                logging_integration,
            ]

            # Initialize Sentry
            sentry_sdk.init(
                dsn=self.settings.sentry_dsn,
                environment=self.settings.sentry_environment,
                sample_rate=self.settings.sentry_sample_rate,
                traces_sample_rate=self.settings.sentry_traces_sample_rate,
                integrations=integrations,
                # Add additional context
                before_send=self._before_send,
                # Add request data
                send_default_pii=False,  # Don't send personally identifiable information
            )

            self.sentry = sentry_sdk
            self.enabled = True
            self.logger.info(f"Sentry initialized for environment: {self.settings.sentry_environment}")

        except ImportError as e:
            self.logger.info(
                f"Sentry SDK not installed or incomplete: {e}. To enable Sentry, install with: pip install sentry-sdk[fastapi]"
            )
            self.enabled = False
        except Exception as e:
            self.logger.error(f"Failed to initialize Sentry: {e}")
            self.enabled = False

    def _before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Filter and enhance events before sending to Sentry
        """
        # Don't send events in development unless explicitly configured
        if self.settings.app_env == "dev" and self.settings.sentry_sample_rate == 0.0:
            return None

        self._clean_event_ansi_codes(event)

        event.setdefault("tags", {})["framework"] = "framefox"

        if "request" in event.get("contexts", {}):
            request_data = event["contexts"]["request"]
            if "headers" in request_data:
                sensitive_headers = [
                    "authorization",
                    "cookie",
                    "x-api-key",
                    "x-csrf-token",
                ]
                for header in sensitive_headers:
                    if header in request_data["headers"]:
                        request_data["headers"][header] = "[Filtered]"

        if "extra" in event:
            extra = event["extra"]
            sensitive_keys = ["password", "token", "secret", "key", "auth"]
            for key in list(extra.keys()):
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    extra[key] = "[Filtered]"

        return event

    def _clean_event_ansi_codes(self, event: Dict[str, Any]):
        """Recursively clean ANSI codes from event data"""
        if isinstance(event, dict):
            for key, value in event.items():
                if isinstance(value, str):
                    event[key] = AnsiCleaner.clean(value)
                elif isinstance(value, (dict, list)):
                    self._clean_event_ansi_codes(value)
        elif isinstance(event, list):
            for i, item in enumerate(event):
                if isinstance(item, str):
                    event[i] = AnsiCleaner.clean(item)
                elif isinstance(item, (dict, list)):
                    self._clean_event_ansi_codes(item)

    def is_enabled(self) -> bool:
        """Check if Sentry is enabled and configured"""
        return self.enabled

    def capture_exception(self, exception: Exception, **kwargs):
        """Capture an exception and send it to Sentry"""
        if not self.enabled or not self.sentry:
            return

        try:
            clean_kwargs = self._clean_kwargs(kwargs)
            self.sentry.capture_exception(exception, **clean_kwargs)
        except Exception as e:
            self.logger.error(f"Failed to capture exception in Sentry: {e}")

    def capture_message(self, message: str, level: str = "info", **kwargs):
        """Capture a message and send it to Sentry"""
        if not self.enabled or not self.sentry:
            return

        try:
            clean_message = AnsiCleaner.clean(message)
            clean_kwargs = self._clean_kwargs(kwargs)
            self.sentry.capture_message(clean_message, level=level, **clean_kwargs)
        except Exception as e:
            self.logger.error(f"Failed to capture message in Sentry: {e}")

    def _clean_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Clean ANSI codes from kwargs"""
        clean_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                clean_kwargs[key] = AnsiCleaner.clean(value)
            elif isinstance(value, (dict, list)):
                clean_kwargs[key] = value
                self._clean_event_ansi_codes(clean_kwargs[key])
            else:
                clean_kwargs[key] = value
        return clean_kwargs

    def add_breadcrumb(
        self,
        message: str,
        category: str = "custom",
        level: str = "info",
        data: Optional[Dict] = None,
    ):
        """Add a breadcrumb for debugging context"""
        if not self.enabled or not self.sentry:
            return

        try:

            clean_message = AnsiCleaner.clean(message)
            clean_data = data or {}
            self._clean_event_ansi_codes(clean_data)

            self.sentry.add_breadcrumb(message=clean_message, category=category, level=level, data=clean_data)
        except Exception as e:
            self.logger.error(f"Failed to add breadcrumb in Sentry: {e}")

    def set_user(self, user_data: Dict[str, Any]):
        """Set user context for Sentry"""
        if not self.enabled or not self.sentry:
            return

        try:
            filtered_data = {}
            for key, value in user_data.items():
                if key.lower() in ["password", "token", "secret", "auth_token"]:
                    filtered_data[key] = "[Filtered]"
                else:
                    filtered_data[key] = AnsiCleaner.clean(str(value)) if isinstance(value, str) else value

            self.sentry.set_user(filtered_data)
        except Exception as e:
            self.logger.error(f"Failed to set user context in Sentry: {e}")

    def set_tag(self, key: str, value: str):
        """Set a tag for Sentry"""
        if not self.enabled or not self.sentry:
            return

        try:
            clean_value = AnsiCleaner.clean(str(value))
            self.sentry.set_tag(key, clean_value)
        except Exception as e:
            self.logger.error(f"Failed to set tag in Sentry: {e}")

    def set_context(self, key: str, context: Dict[str, Any]):
        """Set additional context for Sentry"""
        if not self.enabled or not self.sentry:
            return

        try:
            # Nettoyer le contexte
            clean_context = context.copy()
            self._clean_event_ansi_codes(clean_context)
            self.sentry.set_context(key, clean_context)
        except Exception as e:
            self.logger.error(f"Failed to set context in Sentry: {e}")

    def start_transaction(self, name: str, op: str = "http.server"):
        """Start a new Sentry transaction for performance monitoring"""
        if not self.enabled or not self.sentry:
            return None

        try:
            clean_name = AnsiCleaner.clean(name)
            return self.sentry.start_transaction(name=clean_name, op=op)
        except Exception as e:
            self.logger.error(f"Failed to start Sentry transaction: {e}")
            return None

    def finish_transaction(self, transaction, status: str = "ok"):
        """Finish a Sentry transaction"""
        if not self.enabled or not transaction:
            return

        try:
            transaction.set_status(status)
            transaction.finish()
        except Exception as e:
            self.logger.error(f"Failed to finish Sentry transaction: {e}")
