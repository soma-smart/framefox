import os
from framefox.terminal.common.class_name_manager import ClassNameManager


class ModelChecker:
    def __init__(self):
        self.entity_path = r'src/entity'
        self.repositories_path = r'src/repository'

    def check_entity_file(self, entity_name: str):
        """
        Check if the entity exists.

        Args:
            entity_name (str): The name of the entity in snake_case.

        Returns:
            bool: True if the entity does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            print("Invalid name. Must be in snake_case.")
            return False
        entity_file_name = entity_name + ".py"
        entity_path = os.path.join(self.entity_path, entity_file_name)
        if not os.path.exists(entity_path):
            print(f"Entity file '{entity_name}' does not exist.")
            return False
        # print(f"Entity file '{entity_name}' exists.")
        return True

    def check_repository_file(self, entity_name: str):
        """
        Check if the repository exists.

        Args:
            entity_name (str): The name of the entity in snake_case.

        Returns:
            bool: True if the repository does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            print("Invalid name. Must be in snake_case.")
            return False
        repository_file_name = entity_name + "_repository.py"
        repository_path = os.path.join(
            self.repositories_path, repository_file_name)
        if not os.path.exists(repository_path):
            print(f"Repository file '{repository_file_name}' does not exist.")
            return False
        # print(f"Repository file '{repository_file_name}' exists.")
        return True

    def check_entity_class(self, entity_name: str):
        """
        Check if the entity class exists.

        Args:
            entity_name (str): The name of the entity in snake_case.

        Returns:
            bool: True if the entity class does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            print("Invalid name. Must be in snake_case.")
            return False
        entity_class_name = ClassNameManager.snake_to_pascal(entity_name)
        entity_file_name = entity_name + ".py"
        entity_path = os.path.join(self.entity_path, entity_file_name)
        if not os.path.exists(entity_path):
            print(f"Entity file {entity_name} does not exist.")
            return False
        with open(entity_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "class" in line and entity_class_name in line:
                    # print(f"Entity class '{entity_class_name}' exists.")
                    return True
        print(f"Entity class '{entity_class_name}' does not exist.")
        return False

    def check_repository_class(self, repository_name: str):
        """
        Check if the repository class exists.

        Args:
            repository_name (str): The name of the repository in snake_case.

        Returns:
            bool: True if the repository class does not exist, False otherwise.
        """
        if not ClassNameManager.is_snake_case(repository_name):
            print("Invalid name. Must be in snake_case.")
            return False
        repository_class_name = ClassNameManager.snake_to_pascal(
            repository_name) + "Repository"
        repository_file_name = repository_name + "_repository.py"
        repository_path = os.path.join(
            self.repositories_path, repository_file_name)
        if not os.path.exists(repository_path):
            print(f"Repository file {repository_file_name} does not exist.")
            return False
        with open(repository_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "class" in line and repository_class_name in line:
                    # print(f"Repository class '{
                    #       repository_class_name}' exists.")
                    return True
        print(f"Repository class '{repository_class_name}' does not exist.")
        return False

    def check_entity_and_repository(self, entity_name: str):
        """
        Check if the entity and repository exist.

        Args:
            entity_name (str): The name of the entity in snake_case.

        Returns:
            bool: True if the entity and repository do not exist, False otherwise.
        """
        return self.check_entity_file(entity_name) and\
            self.check_repository_file(entity_name) and\
            self.check_entity_class(entity_name) and\
            self.check_repository_class(entity_name)
