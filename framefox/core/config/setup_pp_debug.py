import builtins
from framefox.core.debug.pp import pp


def setup_pp_debug():
    builtins.pp = pp
