from typer import Typer

from .cache_clear_command import CacheClearCommand
from .cache_warmup_command import CacheWarmupCommand


def add_cache_commands(app: Typer) -> None:
    cache_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @cache_commands.command()
    def clear():
        """
        Clear all cache files and directories
        """
        CacheClearCommand().execute()

    @cache_commands.command()
    def warmup():
        """
        Warm up the application cache
        """
        CacheWarmupCommand().execute()

    app.add_typer(
        cache_commands,
        name="cache",
        help="Cache operations like clearing cache files and directories.",
    )