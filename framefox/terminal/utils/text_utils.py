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
    """Suggest similar commands based on Levenshtein distance"""
    suggestions = []
    for command in available_commands:
        distance = levenshtein_distance(target, command)
        if distance <= threshold:
            suggestions.append((command, distance))

    # Sort by distance (closest first)
    suggestions.sort(key=lambda x: x[1])
    return [cmd for cmd, _ in suggestions]
