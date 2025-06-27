import inspect

import typer

from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.typer_config.command_builder import CommandBuilder
from framefox.terminal.ui.display_manager import DisplayManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class AppConfigurator:
    """
    Configures the main Typer application with intelligent command handling.
    This class is responsible for setting up the Typer CLI application, including:
    - Registering built-in and custom commands.
    - Automatically detecting command signatures to enable Typer's parameter parsing.
    - Organizing commands into groups and subcommands.
    - Managing display and help output via a DisplayManager.
    - Handling safe instantiation and execution of command classes.
    """

    def __init__(self, registry: CommandRegistry, display_manager: DisplayManager):
        self.registry = registry
        self.display_manager = display_manager
        self.command_builder = CommandBuilder(registry, display_manager)

        self.app = typer.Typer(
            name="Framefox",
            help="🦊 Framefox - Swift, smart, and a bit foxy",
            no_args_is_help=False,
            rich_markup_mode="rich",
            pretty_exceptions_enable=False,
            add_completion=True,
            pretty_exceptions_show_locals=False,
        )

    def configure(self) -> typer.Typer:
        self._setup_main_callback()
        self._setup_builtin_commands()
        self._setup_command_groups_intelligent()
        return self.app

    def _setup_main_callback(self):
        @self.app.callback(invoke_without_command=True)
        def main(
            ctx: typer.Context,
            help: bool = typer.Option(None, "--help", "-h", is_eager=True),
            all: bool = typer.Option(False, "--all", "-a"),
        ):
            if ctx.invoked_subcommand is None:
                self.display_manager.print_header()
                command_groups = self.registry.get_command_groups()

                if all:
                    self.display_manager.display_all_commands(command_groups)
                else:
                    self.display_manager.display_help(command_groups)

                raise typer.Exit()

    def _setup_builtin_commands(self):
        @self.app.command("list")
        def list_commands():
            self.display_manager.print_header()
            command_groups = self.registry.get_command_groups()
            self.display_manager.display_all_commands(command_groups)

        @self.app.command("init")
        def init():
            init_command_class = self.registry.get_command("init")
            if init_command_class:
                try:
                    instance = self._safe_instantiate(init_command_class, "init")
                    if instance:
                        return instance.execute()
                except Exception as e:
                    self.display_manager.print_error(f"Error executing init command: {e}")
                    return 1
            else:
                self.display_manager.print_error("Init command not available")
                return 1

        @self.app.command("star-us")
        def star_us():
            star_us_command_class = self.registry.get_command("star-us")
            if star_us_command_class:
                try:
                    instance = self._safe_instantiate(star_us_command_class, "star-us")
                    if instance:
                        return instance.execute()
                except Exception as e:
                    self.display_manager.print_error(f"Error executing star-us command: {e}")
                    return 1
            else:
                self.display_manager.print_error("Star-us command not available")
                return 1

    def _setup_command_groups_intelligent(self):
        command_groups_meta = self.registry.list_all_commands()

        for namespace, command_names in command_groups_meta.items():
            if namespace == "main":
                for command_name in command_names:
                    if command_name not in ["init", "list", "star-us"]:
                        self._add_root_command_intelligent(command_name)
                continue

            subapp = self._create_subapp_intelligent(namespace, command_names)
            self.app.add_typer(subapp, name=namespace)

    def _add_root_command_intelligent(self, command_name: str):
        command_class = self.registry.get_command(command_name)
        if not command_class:
            print(f"⚠️ WARNING: Could not resolve root command '{command_name}'")
            return

        if self._command_has_typer_params(command_class):
            self._add_typer_root_command_with_params(command_name, command_class)
        else:
            self._add_simple_root_command(command_name, command_class)

    def _create_subapp_intelligent(self, namespace: str, command_names: list) -> typer.Typer:
        description = self._get_namespace_description(namespace)

        subapp = typer.Typer(
            name=namespace,
            help=description,
            no_args_is_help=False,
        )

        @subapp.callback(invoke_without_command=True)
        def subgroup_main(ctx: typer.Context):
            if ctx.invoked_subcommand is None:
                self.display_manager.print_header()
                commands_dict = {}
                for cmd_name in command_names:
                    cmd_class = self.registry.get_command(cmd_name)
                    if cmd_class:
                        commands_dict[cmd_name] = cmd_class

                self.display_manager.display_subgroup_help(namespace, commands_dict, description)
                raise typer.Exit()

        for command_name in command_names:
            command_class = self.registry.get_command(command_name)
            if not command_class:
                print(f"⚠️ WARNING: Could not resolve command '{command_name}'")
                continue

            if self._command_has_typer_params(command_class):
                self._add_typer_command_with_params(subapp, command_name, command_class)
            else:
                self._add_simple_command(subapp, command_name, command_class)

        return subapp

    def _command_has_typer_params(self, command_class) -> bool:
        try:
            # Vérifier la signature de la méthode execute sans instancier la classe
            execute_method = getattr(command_class, "execute", None)
            if not execute_method:
                return False

            sig = inspect.signature(execute_method)

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                if param.annotation != inspect.Parameter.empty:
                    return True

                if hasattr(param.default, "__module__") and "typer" in str(param.default):
                    return True

            return False
        except Exception:
            return False

    def _add_typer_command_with_params(self, subapp: typer.Typer, command_name: str, command_class):
        def create_typer_wrapper():
            instance = self._safe_instantiate(command_class, command_name)
            if not instance:

                def error_func(*args, **kwargs):
                    self.display_manager.print_error(f"Could not instantiate {command_name}")
                    return 1

                return error_func

            return instance.execute

        wrapper_func = create_typer_wrapper()
        subapp.command(name=command_name)(wrapper_func)

    def _add_typer_root_command_with_params(self, command_name: str, command_class):
        def create_typer_wrapper():
            instance = self._safe_instantiate(command_class, command_name)
            if not instance:

                def error_func(*args, **kwargs):
                    self.display_manager.print_error(f"Could not instantiate {command_name}")
                    return 1

                return error_func

            return instance.execute

        wrapper_func = create_typer_wrapper()
        self.app.command(name=command_name)(wrapper_func)

    def _add_simple_command(self, subapp: typer.Typer, command_name: str, command_class):
        def command_executor():
            instance = self._safe_instantiate(command_class, command_name)
            if instance:
                return instance.execute()
            return 1

        command_executor.__name__ = f"execute_{command_name}"
        command_executor.__doc__ = f"Execute {command_name} command"

        subapp.command(name=command_name)(command_executor)

    def _add_simple_root_command(self, command_name: str, command_class):
        def command_executor():
            instance = self._safe_instantiate(command_class, command_name)
            if instance:
                return instance.execute()
            return 1

        command_executor.__name__ = f"execute_{command_name}"
        command_executor.__doc__ = f"Execute {command_name} command"

        self.app.command(name=command_name)(command_executor)

    def _safe_instantiate(self, command_class, command_name: str):
        try:
            try:
                instance = command_class()
                if hasattr(instance, "name") and not getattr(instance, "name", None):
                    instance.name = command_name
                return instance
            except TypeError:
                try:
                    return command_class(command_name)
                except Exception:
                    print(f"Could not instantiate {command_class.__name__}")
                    return None
        except Exception as e:
            # Pour les exceptions Framefox, les re-lancer
            from framefox.core.debug.exception.base_exception import FramefoxException

            if isinstance(e, FramefoxException):
                raise e
            # Pour les autres exceptions, les afficher et retourner None
            self.display_manager.print_error(f"Failed to instantiate {command_name}: {e}")
            return None

    def _get_namespace_description(self, namespace: str) -> str:
        descriptions = {
            "create": "Create various resources like entities or CRUD operations.",
            "debug": "Debug operations like checking routes or testing security.",
            "database": "Database operations like creating or migrating databases.",
            "cache": "Cache operations like clearing cache files and directories.",
            "mock": "Mock operations like generating or loading mock data.",
            "server": "Server operations like starting or stopping the server.",
            "main": "Main operations",
        }
        return descriptions.get(namespace, f"{namespace.title()} operations")
