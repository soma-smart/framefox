from urllib.parse import parse_qs, urlparse

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class MailUrlParser:
    """Parser for mail configuration URLs"""

    @staticmethod
    def parse_url(url_string: str) -> dict:
        """
        Parse a URL in the format smtp://username:password@host:port?tls=true

        Args:
            url_string: Mail configuration URL

        Returns:
            Dictionary with extracted parameters
        """
        if not url_string:
            return {
                "host": "localhost",
                "port": 25,
                "username": "",
                "password": "",
                "use_tls": False,
                "use_ssl": False,
            }

        parsed_url = urlparse(url_string)
        is_ssl = parsed_url.scheme == "smtps"
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or (465 if is_ssl else 587)
        username = parsed_url.username or ""
        password = parsed_url.password or ""
        query_params = parse_qs(parsed_url.query)

        result = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "use_tls": not is_ssl,
            "use_ssl": is_ssl,
        }

        if "tls" in query_params:
            result["use_tls"] = query_params["tls"][0].lower() == "true"
        if "ssl" in query_params:
            result["use_ssl"] = query_params["ssl"][0].lower() == "true"

        return result
