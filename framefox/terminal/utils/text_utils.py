"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    This function determines the minimum number of operations (insertion, deletion, substitution)
    needed to transform one string into another.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def suggest_similar_commands(
    target: str, available_commands: list, threshold: int = 3
) -> list:
    """Suggest similar commands based on Levenshtein distance with smart scoring"""
    if not target or not available_commands:
        return []

    suggestions = []
    target_lower = target.lower()

    for command in available_commands:
        command_lower = command.lower()

        # Exact match (shouldn't happen in error context, but just in case)
        if target_lower == command_lower:
            continue

        # Calculate base distance
        distance = levenshtein_distance(target_lower, command_lower)

        # Smart scoring: give bonus for common mistakes
        score = distance

        # Bonus for commands that start with the same letter(s)
        if target_lower and command_lower.startswith(target_lower[0]):
            score -= 0.5

        # Bonus for length similarity
        length_diff = abs(len(target) - len(command))
        if length_diff <= 2:
            score -= 0.3

        # Bonus for substring matches
        if target_lower in command_lower or command_lower in target_lower:
            score -= 1

        # Only include if within threshold
        if score <= threshold:
            suggestions.append((command, score))

    # Sort by score (best matches first)
    suggestions.sort(key=lambda x: x[1])
    return [cmd for cmd, _ in suggestions[:5]]  # Return top 5 matches


def calculate_similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity ratio between two strings (0.0 to 1.0)"""
    if not s1 or not s2:
        return 0.0

    max_len = max(len(s1), len(s2))
    distance = levenshtein_distance(s1.lower(), s2.lower())

    return 1.0 - (distance / max_len)
