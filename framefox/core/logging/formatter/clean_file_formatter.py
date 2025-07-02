import logging

from framefox.core.logging.utils.ansi_cleaner import AnsiCleaner

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CleanFileFormatter(logging.Formatter):
    """
    File formatter that removes ANSI color codes from log messages
    """

    def format(self, record):
        formatted = super().format(record)
        return AnsiCleaner.clean(formatted)
