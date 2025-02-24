"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class DebugException(Exception):
    def __init__(self, content: str):
        self.content = content
