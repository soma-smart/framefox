import builtins
<<<<<<< Updated upstream:src/core/config/setup_pp_debug.py
from src.core.debug.pp import pp
=======

from framefox.core.debug.pp import pp
>>>>>>> Stashed changes:framefox/core/config/setup_pp_debug.py


def setup_pp_debug():
    builtins.pp = pp
