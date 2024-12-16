from flask import Response


class InvalidInputException(Response):
    def __init__(self, message):
        super().__init__(message, status=400)
