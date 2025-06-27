import os
from pathlib import Path
from typing import Any, Dict

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class ConfigCommand(AbstractCommand):
    """Command to display all environment and YAML configuration"""

    def __init__(self):
        super().__init__("config")

    def execute(self):
        """Display all configuration (environment variables and YAML files)"""
        console = Console()

        # Display environment variables
        self._display_environment_variables(console)

        # Display YAML configuration files
        self._display_yaml_configurations(console)

        # Display merged configuration summary
        self._display_configuration_summary(console)

    def _display_environment_variables(self, console: Console):
        """Display environment variables section"""
        console.print()
        console.print(Panel.fit("[bold orange1]Environment Variables[/bold orange1]", border_style="orange1"))

        # Get Framefox-related environment variables
        framefox_env_vars = self._get_framefox_env_vars()

        if not framefox_env_vars:
            console.print("[dim]No Framefox-related environment variables found[/dim]")
            return

        table = Table(show_header=True, header_style="bold orange3")
        table.add_column("Variable", style="bold orange3", width=25)
        table.add_column("Value", style="white", width=50)
        table.add_column("Source", style="dim", width=10)

        for var_name, var_value in framefox_env_vars.items():
            # Mask sensitive values
            display_value = self._mask_sensitive_value(var_name, var_value)
            source = "ENV" if var_name in os.environ else ".env"
            table.add_row(var_name, display_value, source)

        console.print(table)

    def _display_yaml_configurations(self, console: Console):
        """Display YAML configuration files section"""
        console.print()
        console.print(Panel.fit("[bold orange1]YAML Configuration Files[/bold orange1]", border_style="orange1"))

        config_dir = Path("config")
        if not config_dir.exists():
            console.print("[dim]No config directory found[/dim]")
            return

        yaml_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))

        if not yaml_files:
            console.print("[dim]No YAML configuration files found[/dim]")
            return

        for yaml_file in sorted(yaml_files):
            self._display_yaml_file(console, yaml_file)

    def _display_yaml_file(self, console: Console, yaml_file: Path):
        """Display content of a single YAML file"""
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f) or {}

            # Create a panel for this YAML file
            file_name = yaml_file.name
            console.print()
            console.print(f"[bold orange3]{file_name}[/bold orange3]", style="bold")
            console.print("─" * 60, style="dim")

            if not content:
                console.print("[dim]  (empty or no valid YAML content)[/dim]")
                return

            # Display the YAML content in a formatted way
            self._display_yaml_content(console, content, indent=0)

        except yaml.YAMLError as e:
            console.print(f"[red]  Error parsing {yaml_file.name}: {e}[/red]")
        except FileNotFoundError:
            console.print(f"[red]  File not found: {yaml_file.name}[/red]")
        except Exception as e:
            console.print(f"[red]  Error reading {yaml_file.name}: {e}[/red]")

    def _display_yaml_content(self, console: Console, content: Dict[str, Any], indent: int = 0):
        """Recursively display YAML content with proper formatting"""
        spacing = "  " * indent

        for key, value in content.items():
            if isinstance(value, dict):
                # Section header
                console.print(f"{spacing}[bold bright_cyan]{key}:[/bold bright_cyan]")
                self._display_yaml_content(console, value, indent + 1)
            elif isinstance(value, list):
                console.print(f"{spacing}[bold bright_cyan]{key}:[/bold bright_cyan]")
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        console.print(f"{spacing}  [dim]#{i}[/dim]")
                        self._display_yaml_content(console, item, indent + 2)
                    else:
                        # Format list items with bullets
                        display_value = self._mask_sensitive_value(f"{key}_{i}", str(item))
                        if str(item).strip() == "*":
                            console.print(f"{spacing}  [yellow]•[/yellow] [bright_yellow]{display_value}[/bright_yellow]")
                        else:
                            console.print(f"{spacing}  [green]•[/green] [white]{display_value}[/white]")
            else:
                # Handle different value types with appropriate styling
                display_value = self._mask_sensitive_value(key, str(value))
                value_style = self._get_value_style(value, key)
                console.print(
                    f"{spacing}[bold bright_cyan]{key}:[/bold bright_cyan] {value_style}{display_value}[/{value_style.replace('[', '').replace(']', '')}]"
                )

    def _get_value_style(self, value: Any, key: str) -> str:
        """Get appropriate styling for different value types"""
        if value is None or str(value).lower() in ["none", "null"]:
            return "[dim italic]"
        elif isinstance(value, bool):
            return "[green]" if value else "[red]"
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            return "[cyan]"
        elif str(value).startswith("${") and str(value).endswith("}"):
            return "[yellow]"  # Environment variables
        elif key.lower() in ["url", "path", "dir", "file_path"]:
            return "[blue]"
        elif key.lower() in ["password", "secret", "key", "token"]:
            return "[red]"
        else:
            return "[white]"

    def _display_configuration_summary(self, console: Console):
        """Display a summary of the configuration"""
        console.print()
        console.print(Panel.fit("[bold orange1]Configuration Summary[/bold orange1]", border_style="orange1"))

        # Count environment variables
        framefox_env_vars = self._get_framefox_env_vars()
        env_count = len(framefox_env_vars)

        # Count YAML files
        config_dir = Path("config")
        yaml_count = 0
        if config_dir.exists():
            yaml_count = len(list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml")))

        # Display summary table
        table = Table(show_header=True, header_style="bold orange3")
        table.add_column("Configuration Type", style="bold orange3")
        table.add_column("Count", style="white")
        table.add_column("Status", style="white")

        env_status = "[green]Loaded[/green]" if env_count > 0 else "[yellow]None found[/yellow]"
        yaml_status = "[green]Available[/green]" if yaml_count > 0 else "[yellow]None found[/yellow]"

        table.add_row("Environment Variables", str(env_count), env_status)
        table.add_row("YAML Configuration Files", str(yaml_count), yaml_status)

        console.print(table)

        # Additional information
        console.print()
        console.print("[dim]Tip: Environment variables override YAML configuration values[/dim]")

    def _get_framefox_env_vars(self) -> Dict[str, str]:
        """Get Framefox-related environment variables"""
        # Load from .env file if it exists
        env_vars = {}

        # First, load from .env file
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip()
            except Exception:
                pass

        # Then, override with actual environment variables
        framefox_prefixes = ["APP_", "DATABASE_", "MAIL_", "RABBITMQ_", "SESSION_"]
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in framefox_prefixes):
                env_vars[key] = value

        return env_vars

    def _mask_sensitive_value(self, key: str, value: str) -> str:
        """Mask sensitive configuration values"""
        sensitive_keys = ["password", "secret", "key", "token", "api_key", "database_url", "mail_url", "rabbitmq_url"]

        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            if len(value) <= 8:
                return "*" * len(value)
            else:
                return value[:3] + "*" * (len(value) - 6) + value[-3:]

        return value
