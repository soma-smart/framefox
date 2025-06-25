from urllib.parse import urlparse

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphael
Github: https://github.com/Vasulvius 
"""


class DatabaseUrlParser:
    @staticmethod
    def parse(database_url: str):
        parsed_url = urlparse(database_url)
        scheme = parsed_url.scheme
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]

        return scheme, user, password, host, port, database
