from urllib.parse import urlparse


class DatabaseUrlParser:
    @staticmethod
    def parse_database_url(database_url: str):
        # Analyse l'URL
        parsed_url = urlparse(database_url)

        # Récupère les composants nécessaires
        scheme = parsed_url.scheme
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]

        return scheme, user, password, host, port, database
