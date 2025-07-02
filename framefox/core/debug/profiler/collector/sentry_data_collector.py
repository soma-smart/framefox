from typing import Any, Dict

from fastapi import Request, Response

from framefox.core.config.settings import Settings
from framefox.core.debug.profiler.collector.data_collector import DataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SentryDataCollector(DataCollector):
    """
    Data collector for Sentry integration information.

    Collects information about Sentry configuration and status
    for display in the profiler.
    """

    def __init__(self):
        super().__init__("sentry", "fa-map-signs")
        self.settings = Settings()
        self.sentry_manager = None

        if self.settings.sentry_enabled:
            try:
                from framefox.core.debug.sentry.sentry_manager import SentryManager

                self.sentry_manager = SentryManager()
            except ImportError:
                pass

    def collect(self, request: Request, response: Response):
        """Collect Sentry-related data"""
        if not self.settings.sentry_enabled:
            self.data = {
                "enabled": False,
                "dsn_configured": False,
                "status": "not_configured",
                "reason": "Sentry configuration is commented out in debug.yaml",
            }
            return

        if not self.sentry_manager:
            self.data = {
                "enabled": False,
                "dsn_configured": bool(self.settings.sentry_dsn),
                "environment": self.settings.sentry_environment,
                "sample_rate": self.settings.sentry_sample_rate,
                "traces_sample_rate": self.settings.sentry_traces_sample_rate,
                "status": "sdk_not_installed",
                "reason": "Sentry SDK not installed. Run: pip install sentry-sdk[fastapi]",
            }
            return

        self.data = {
            "enabled": self.sentry_manager.is_enabled(),
            "dsn_configured": bool(self.settings.sentry_dsn),
            "environment": self.settings.sentry_environment,
            "sample_rate": self.settings.sentry_sample_rate,
            "traces_sample_rate": self.settings.sentry_traces_sample_rate,
        }

        if self.sentry_manager.is_enabled():
            self.data["status"] = "active"
        elif self.settings.sentry_dsn:
            self.data["status"] = "configured_but_inactive"
        else:
            self.data["status"] = "not_configured"

    def get_data(self) -> Dict[str, Any]:
        """Return collected Sentry data"""
        return self.data

    def reset(self):
        """Reset collected data"""
        self.data = {}
