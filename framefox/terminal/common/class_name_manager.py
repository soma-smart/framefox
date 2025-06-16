import re

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphael
Github: https://github.com/Vasulvius 
"""

class ClassNameManager:
    @staticmethod
    def is_snake_case(name: str) -> bool:
        return bool(re.match(r"^[a-z]+(_[a-z]+)*$", name))

    @staticmethod
    def snake_to_pascal(name: str) -> str:
        return "".join([word.capitalize() for word in name.split("_")])
