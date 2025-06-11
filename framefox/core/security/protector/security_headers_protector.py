import os

from fastapi import Request, Response

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SecurityHeadersProtector:
    """
    Adaptive security headers that adjust based on environment.

    This class provides environment-aware security headers for web applications.
    In production mode, it applies strict security policies, while in development
    mode it uses more lenient settings to facilitate development workflow.

    Attributes:
        strict_mode (bool): Whether to apply strict security headers (production mode).
                           Auto-detected from APP_ENV environment variable if not specified.
    """

    def __init__(self, strict_mode: bool = None):
        if strict_mode is None:
            self.strict_mode = os.getenv("APP_ENV", "dev") == "prod"
        else:
            self.strict_mode = strict_mode

    def apply_headers(self, response: Response, request: Request) -> None:
        """Apply environment-appropriate security headers."""

        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if self.strict_mode:
            response.headers["X-Frame-Options"] = "DENY"
        else:
            response.headers["X-Frame-Options"] = "SAMEORIGIN"

        if self.strict_mode:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                "connect-src 'self'",
                "media-src 'self'",
                "object-src 'self'",
                "child-src 'self'",
                "worker-src 'self'",
                "form-action 'self'",
                "base-uri 'self'",
                "upgrade-insecure-requests",
            ]
        else:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' localhost:* 127.0.0.1:*",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https: http:",
                "font-src 'self' data: https:",
                "connect-src 'self' localhost:* 127.0.0.1:* ws: wss:",
                "media-src 'self' data:",
                "object-src 'self' data:",
                "child-src 'self' localhost:*",
                "worker-src 'self' blob:",
                "form-action 'self'",
            ]

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        if self.strict_mode and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        permissions = [
            "camera=(self)",
            "microphone=(self)",
            "geolocation=(self)",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "accelerometer=()",
            "gyroscope=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        if self._is_highly_sensitive_path(request.url.path):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        if not self.strict_mode:
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        else:
            response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    def _is_highly_sensitive_path(self, path: str) -> bool:
        """Only the most sensitive paths get strict cache control."""
        highly_sensitive = [
            "/login",
            "/logout",
            "/password",
            "/api/auth",
            "/admin/users",
            "/admin/settings",
        ]
        return any(pattern in path.lower() for pattern in highly_sensitive)
