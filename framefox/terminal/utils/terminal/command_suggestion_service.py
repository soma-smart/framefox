from typing import List, Optional, Tuple

from framefox.terminal.utils.text_utils import suggest_similar_commands


class CommandSuggestionService:
    """
    Service for generating intelligent command suggestions based on user input
    """

    def __init__(self, command_registry):
        self.command_registry = command_registry

    def suggest_command_with_subcommand(self, args: List[str]) -> Optional[Tuple[str, str]]:
        """
        Suggest a complete command with subcommand from partial input

        Args:
            args: User input arguments

        Returns:
            Tuple of (error_message, suggestion) or None if no suggestion
        """
        if len(args) < 2:
            return None

        main_command = args[0]
        potential_subcommand = args[1]

        command_groups = self.command_registry.get_command_groups()
        available_groups = [group for group in command_groups.keys() if group != "main"]
        available_groups.extend(["init", "list"])

        # Find best matching group
        group_suggestions = suggest_similar_commands(main_command, available_groups, threshold=3)

        if not group_suggestions:
            return None

        best_group = group_suggestions[0]

        # Handle case with no subcommand
        if not potential_subcommand:
            error_msg = f"Unknown command: '{' '.join(args)}'"
            return (error_msg, best_group)

        # Find best subcommand match
        if best_group in command_groups:
            available_subcommands = list(command_groups[best_group].keys())
            best_subcommand = self._find_best_subcommand_match(potential_subcommand, available_subcommands)

            error_msg = f"Unknown command: '{' '.join(args)}'"

            if best_subcommand:
                full_suggestion = f"{best_group} {best_subcommand}"
                return (error_msg, full_suggestion)
            else:
                # Group exists but no good subcommand match
                return (error_msg, f"group:{best_group}", available_subcommands)

        return None

    def _find_best_subcommand_match(self, target_subcommand: str, available_subcommands: List[str]) -> Optional[str]:
        """
        Find the best matching subcommand using multiple criteria
        """
        target_lower = target_subcommand.lower()

        # 1. Prefix matching
        prefix_matches = [cmd for cmd in available_subcommands if cmd.lower().startswith(target_lower)]
        if prefix_matches:
            return prefix_matches[0]

        # 2. Inclusion matching
        inclusion_matches = [cmd for cmd in available_subcommands if target_lower in cmd.lower()]
        if inclusion_matches:
            return inclusion_matches[0]

        # 3. Levenshtein similarity
        suggestions = suggest_similar_commands(target_subcommand, available_subcommands, threshold=3)
        if suggestions:
            return suggestions[0]

        # 4. Fallback: shortest command (often most basic)
        if available_subcommands:
            return min(available_subcommands, key=len)

        return None
