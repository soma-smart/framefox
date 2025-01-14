import logging


class SQLModelFormatter(logging.Formatter):
    def format(self, record):
        record.name = "SQLMODEL"
        return super().format(record)
