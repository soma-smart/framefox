from urllib.parse import parse_qs, urlparse


class MailUrlParser:
    """Parser pour les URLs de configuration mail"""

    @staticmethod
    def parse_url(url_string: str) -> dict:
        """
        Parse une URL au format smtp://username:password@host:port?tls=true

        Args:
            url_string: URL de configuration mail

        Returns:
            Dictionnaire avec les paramètres extraits
        """
        if not url_string:
            return {
                "host": "localhost",
                "port": 25,
                "username": "",
                "password": "",
                "use_tls": False,
                "use_ssl": False
            }

        parsed_url = urlparse(url_string)

        # Protocole détermine SSL/TLS par défaut
        is_ssl = parsed_url.scheme == "smtps"

        # Extraire host et port
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or (465 if is_ssl else 587)  # Ports par défaut

        # Extraire username et password
        username = parsed_url.username or ""
        password = parsed_url.password or ""

        # Extraire les paramètres de la query string
        query_params = parse_qs(parsed_url.query)

        # Paramètres par défaut (sans from_address)
        result = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "use_tls": not is_ssl,  # TLS par défaut pour SMTP standard
            "use_ssl": is_ssl       # SSL par défaut pour SMTPS
        }

        # Paramètres de la query string (sans from)
        if "tls" in query_params:
            result["use_tls"] = query_params["tls"][0].lower() == "true"
        if "ssl" in query_params:
            result["use_ssl"] = query_params["ssl"][0].lower() == "true"

        return result
