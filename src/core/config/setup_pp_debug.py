import builtins
from src.core.debug.pp import pp


def setup_pp_debug():
    builtins.pp = pp
