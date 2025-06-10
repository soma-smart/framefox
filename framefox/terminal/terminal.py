import contextlib
import os
import sys
from io import StringIO
from typing import List

import typer

from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.typer_config.app_configurator import AppConfigurator
from framefox.terminal.ui.display_manager import DisplayManager
from framefox.terminal.ui.error_handler import ErrorHandler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class Terminal:
    """
    Main application console - Simplified and focused
    """

    def __init__(self):
        self.registry = CommandRegistry()
        self.display_manager = DisplayManager()
        self.error_handler = ErrorHandler(self.display_manager.console, self.display_manager)

        # Discover commands
        self.registry.discover_commands()

        # Configure the Typer app
        configurator = AppConfigurator(self.registry, self.display_manager)
        self.app = configurator.configure()

    def run(self, args: List[str] = None):
        """Run the console application with the given arguments"""
        if args is None:
            args = sys.argv[1:]

        # Special case for 'init' without project
        if self._is_init_only_context(args):
            return self._run_init_command()

        # ✅ NOUVELLE APPROCHE : Capturer la sortie de Typer
        return self._run_with_error_handling(args)

    def _run_with_error_handling(self, args: List[str]) -> int:
        """Run Typer app with custom error handling"""

        # Capturer stderr pour intercepter les messages d'erreur de Typer
        stderr_capture = StringIO()

        try:
            # Rediriger temporairement stderr
            with contextlib.redirect_stderr(stderr_capture):
                return self.app(args)

        except typer.Exit as e:
            # Sortie normale de Typer
            return e.exit_code

        except SystemExit as e:
            # Vérifier si c'est une erreur de commande non trouvée
            captured_error = stderr_capture.getvalue()

            if e.code == 2 and args and self._is_command_not_found_error(captured_error):
                # C'est notre cas : commande non trouvée
                return self._handle_unknown_command(args)

            # Autres erreurs système - afficher le message capturé si nécessaire
            if captured_error and not self._is_command_not_found_error(captured_error):
                self.display_manager.print_error(captured_error.strip())

            return e.code

        except Exception as e:
            self.display_manager.print_error(f"Unexpected error: {e}")
            return 1

    def _is_command_not_found_error(self, error_output: str) -> bool:
        """Check if the error is about a command not found"""
        error_indicators = [
            "No such command",
            "Try '",
            "Usage:",
            "Error",
        ]
        return any(indicator in error_output for indicator in error_indicators)

    def _handle_unknown_command(self, args: List[str]) -> int:
        """Handle unknown command and suggest alternatives"""
        if not args:
            return 2

        command_groups = self.registry.get_command_groups()

        # ✅ NOUVELLE LOGIQUE : Toujours essayer d'abord la suggestion intelligente
        if len(args) >= 2:
            if self._try_suggest_full_command_with_subcommand(args):
                return 1

        # Case 1: Unknown main command (e.g., "framefox srever")
        if len(args) == 1:
            available_groups = [group for group in command_groups.keys() if group != "main"]
            available_groups.extend(["init", "list"])

            if self.error_handler.handle_unknown_command(args[0], available_groups):
                return 1

        # Case 2: Unknown subcommand dans un groupe existant (e.g., "framefox server stort")
        elif len(args) == 2:
            group_name, subcommand = args[0], args[1]

            # Check if group exists
            if group_name in command_groups:
                available_subcommands = list(command_groups[group_name].keys())
                if self.error_handler.handle_unknown_subcommand(group_name, subcommand, available_subcommands):
                    return 1

        # Fallback: use styled general error
        self.error_handler.handle_general_error(args)
        return 1

    def _try_suggest_full_command_with_subcommand(self, args: List[str]) -> bool:
        """
        Try to suggest a full command when the user types something like 'created auth'
        """
        from framefox.terminal.utils.text_utils import suggest_similar_commands

        command_groups = self.registry.get_command_groups()
        main_command = args[0]
        potential_subcommand = args[1] if len(args) > 1 else None

        # Get all available main command groups
        available_groups = [group for group in command_groups.keys() if group != "main"]
        available_groups.extend(["init", "list"])

        # Find the best matching group for the main command
        group_suggestions = suggest_similar_commands(main_command, available_groups, threshold=3)

        if not group_suggestions:
            return False

        best_group = group_suggestions[0]

        # ✅ AMÉLIORATION : Si pas de sous-commande, suggérer juste le groupe
        if not potential_subcommand:
            self.error_handler._print_error_header(f"Unknown command: '{' '.join(args)}'")
            self.error_handler._display_single_suggestion(best_group)
            return True

        # ✅ AMÉLIORATION : Chercher la meilleure correspondance de sous-commande
        if best_group in command_groups:
            available_subcommands = list(command_groups[best_group].keys())

            # Calculer le score de correspondance pour chaque sous-commande
            best_subcommand = self._find_best_subcommand_match(potential_subcommand, available_subcommands)

            if best_subcommand:
                # We found both a group and subcommand match!
                full_suggestion = f"{best_group} {best_subcommand}"

                self.error_handler._print_error_header(f"Unknown command: '{' '.join(args)}'")
                self.error_handler._display_single_suggestion(full_suggestion)
                return True
            else:
                # Group matches but no good subcommand match
                self.error_handler._print_error_header(f"Unknown command: '{' '.join(args)}'")
                self.error_handler.display_group_with_available_subcommands(best_group, available_subcommands)
                return True

        return False

    def _find_best_subcommand_match(self, target_subcommand: str, available_subcommands: List[str]) -> str:
        """
        Find the best matching subcommand using multiple criteria
        """
        from framefox.terminal.utils.text_utils import suggest_similar_commands

        # 1. Essayer d'abord la correspondance exacte de préfixe
        target_lower = target_subcommand.lower()

        # Recherche par préfixe
        prefix_matches = [cmd for cmd in available_subcommands if cmd.lower().startswith(target_lower)]
        if prefix_matches:
            return prefix_matches[0]

        # 2. Recherche par inclusion
        inclusion_matches = [cmd for cmd in available_subcommands if target_lower in cmd.lower()]
        if inclusion_matches:
            return inclusion_matches[0]

        # 3. Recherche par similarité Levenshtein
        suggestions = suggest_similar_commands(target_subcommand, available_subcommands, threshold=3)
        if suggestions:
            return suggestions[0]

        # 4. Fallback : prendre la sous-commande la plus courte (souvent la plus basique)
        if available_subcommands:
            return min(available_subcommands, key=len)

        return None

    def _is_init_only_context(self, args: List[str]) -> bool:
        """Check if this is an init-only context"""
        return len(args) == 1 and args[0] == "init" and not os.path.exists("src")

    def _run_init_command(self) -> int:
        """Run the init command directly"""
        command_class = self.registry.get_command("init")
        if not command_class:
            self.display_manager.print_error("Init command not found")
            return 1

        try:
            instance = command_class()
            if instance:
                return instance.execute()
        except Exception as e:
            self.display_manager.print_error(f"Error executing command init: {e}")
            return 1

        return 1
