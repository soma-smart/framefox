import re

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AnsiCleaner:
    """Utility class to clean ANSI color codes from text"""

    ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    @staticmethod
    def clean(text: str) -> str:
        """
        Remove ANSI escape sequences from text

        Args:
            text: Text potentially containing ANSI codes

        Returns:
            Clean text without ANSI codes
        """
        if not text:
            return text

        return AnsiCleaner.ANSI_ESCAPE_PATTERN.sub("", text)

    @staticmethod
    def has_ansi_codes(text: str) -> bool:
        """
        Check if text contains ANSI escape sequences

        Args:
            text: Text to check

        Returns:
            True if text contains ANSI codes
        """
        if not text:
            return False

        return bool(AnsiCleaner.ANSI_ESCAPE_PATTERN.search(text))
