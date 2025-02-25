import logging

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SQLModelFormatter(logging.Formatter):
    def format(self, record):
        record.name = "SQLMODEL"
        return super().format(record)
