import importlib
import os
from typing import Any, Dict, List

from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.printer import Printer


class ModelChecker:
    def __init__(self):
        self.entity_path = r"src/entity"
        self.repositories_path = r"src/repository"
        self.printer = Printer()

    def check_entity_file(self, entity_name: str, verbose: bool = False):
        """
        Check if the entity exists.

        Args:
            entity_name (str): The name of the entity in snake_case.
            verbose (bool): If True, print messages.

        Returns:
            bool: True if the entity does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            if verbose:
                Printer().print_msg("Invalid name. Must be in snake_case.", theme="error")
            return False
        entity_file_name = entity_name + ".py"
        entity_path = os.path.join(self.entity_path, entity_file_name)
        if not os.path.exists(entity_path):
            if verbose:
                Printer().print_msg(
                    f"Entity file '{
                        entity_name}' does not exist.",
                    theme="error",
                )
            return False
        return True

    def check_repository_file(self, entity_name: str, verbose: bool = False):
        """
        Check if the repository exists.

        Args:
            entity_name (str): The name of the entity in snake_case.
            verbose (bool): If True, print messages.

        Returns:
            bool: True if the repository does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            if verbose:
                Printer().print_msg("Invalid name. Must be in snake_case.", theme="error")
            return False
        repository_file_name = entity_name + "_repository.py"
        repository_path = os.path.join(self.repositories_path, repository_file_name)
        if not os.path.exists(repository_path):
            if verbose:
                Printer().print_msg(
                    f"Repository file '{
                        repository_file_name}' does not exist.",
                    theme="error",
                )
            return False
        return True

    def check_entity_class(self, entity_name: str, verbose: bool = False):
        """
        Check if the entity class exists.

        Args:
            entity_name (str): The name of the entity in snake_case.
            verbose (bool): If True, print messages.

        Returns:
            bool: True if the entity class does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            if verbose:
                Printer().print_msg("Invalid name. Must be in snake_case.", theme="error")
            return False
        entity_class_name = ClassNameManager.snake_to_pascal(entity_name)
        entity_file_name = entity_name + ".py"
        entity_path = os.path.join(self.entity_path, entity_file_name)
        if not os.path.exists(entity_path):
            if verbose:
                Printer().print_msg(
                    f"Entity file '{
                        entity_name}' does not exist.",
                    theme="error",
                )
            return False
        with open(entity_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "class" in line and entity_class_name in line:
                    return True
        if verbose:
            Printer().print_msg(
                f"Entity class '{
                    entity_class_name}' does not exist.",
                theme="error",
            )
        return False

    def check_repository_class(self, repository_name: str, verbose: bool = False):
        """
        Check if the repository class exists.

        Args:
            repository_name (str): The name of the repository in snake_case.
            verbose (bool): If True, print messages.

        Returns:
            bool: True if the repository class does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(repository_name):
            if verbose:
                Printer().print_msg("Invalid name. Must be in snake_case.", theme="error")
            return False
        repository_class_name = ClassNameManager.snake_to_pascal(repository_name) + "Repository"
        repository_file_name = repository_name + "_repository.py"
        repository_path = os.path.join(self.repositories_path, repository_file_name)
        if not os.path.exists(repository_path):
            if verbose:
                Printer().print_msg(
                    f"Repository file '{
                        repository_file_name}' does not exist.",
                    theme="error",
                )
            return False
        with open(repository_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "class" in line and repository_class_name in line:
                    return True
        if verbose:
            Printer().print_msg(
                f"Repository class '{
                    repository_class_name}' does not exist.",
                theme="error",
            )
        return False

    def check_entity_and_repository(self, entity_name: str, verbose: bool = False):
        """
        Check if the entity and repository exist.

        Args:
            entity_name (str): The name of the entity in snake_case.
            verbose (bool): If True, print messages.

        Returns:
            bool: True if the entity and repository do not exist, False otherwise.
        """
        return (
            self.check_entity_file(entity_name, verbose)
            and self.check_repository_file(entity_name, verbose)
            and self.check_entity_class(entity_name, verbose)
            and self.check_repository_class(entity_name, verbose)
        )

    def check_entity_property(self, entity_name: str, property_name: str, verbose: bool = False):
        """
        Check if a given property exists for an entity.

        Args:
            entity_name (str): Name of the entity in snake_case format
            property_name (str): Name of the property to check
            verbose (bool, optional): If True, prints error messages. Defaults to False.

        Returns:
            bool: True if the property exists in the entity file, False otherwise

        The method performs the following checks:
        - Validates that entity_name is in snake_case format
        - Verifies that the entity file exists at the specified path
        - Searches for the property_name in the entity file contents
        """
        if not ClassNameManager.is_snake_case(entity_name):
            if verbose:
                Printer().print_msg("Invalid name. Must be in snake_case.", theme="error")
            return False
        entity_file_name = entity_name + ".py"
        entity_path = os.path.join(self.entity_path, entity_file_name)
        if not os.path.exists(entity_path):
            if verbose:
                Printer().print_msg(
                    f"Entity file '{
                        entity_name}' does not exist.",
                    theme="error",
                )
            return False
        with open(entity_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if property_name in line:
                    return True
        if verbose:
            Printer().print_msg(
                f"Property '{
                    property_name}' does not exist.",
                theme="error",
            )
        return False

    def check_entity_properties(self, entity_name: str, properties_name: list, verbose: bool = False):
        """
        Check if multiple properties exist for a specific entity.

        Args:
            entity_name (str): Name of the entity to check
            properties_name (list): List of property names to verify
            verbose (bool, optional): Whether to display verbose output. Defaults to False.

        Returns:
            bool: True if all properties exist for the entity, False otherwise

        Example:
            >>> checker = ModelChecker()
            >>> checker.check_entity_properties("user", ["id", "name"], verbose=True)
            True
        """
        for property_name in properties_name:
            if not self.check_entity_property(entity_name, property_name, verbose):
                return False
        return True

    def check_association_table(self, entity_name: str, target_entity: str, verbose: bool = False) -> bool:
        association_table = f"{entity_name}_{target_entity}_association"
        table_path = os.path.join("src/entity", f"{association_table}.py")
        if not os.path.exists(table_path):
            if verbose:
                Printer().print_msg(
                    f"Association table '{association_table}' does not exist.",
                    theme="error",
                )
            return False
        return True

    def get_entity_properties(self, entity_name: str) -> List[Dict[str, Any]]:
        """Utilise SQLModelInspector pour obtenir les propriétés de l'entité"""
        try:
            import importlib
            import os
            import sys

            from framefox.terminal.common.printer import Printer

            original_path = sys.path.copy()
            project_root = os.getcwd()
            sys.path.insert(0, project_root)

            try:

                entity_module = importlib.import_module(f"src.entity.{entity_name}")
                entity_class_name = ClassNameManager.snake_to_pascal(entity_name)
                entity_class = getattr(entity_module, entity_class_name)

                from framefox.terminal.common.sql_model_inspector import (
                    SQLModelInspector,
                )

                properties = SQLModelInspector.get_entity_properties(entity_class)
                return properties

            finally:

                sys.path = original_path

        except Exception as e:
            Printer().print_msg(
                f"Error getting properties from entity {entity_name}: {str(e)}",
                theme="error",
            )

        return []
