from src.terminal.commands.abstract_command import AbstractCommand
from src.terminal.common.class_name_manager import ClassNameManager


class AddPropertyCommand(AbstractCommand):
    def __init__(self):
        super().__init__('add_property')
        self.entity_folder = r"src/entity"

    def execute(self, name: str, property_name: str, property_type: str, optional: str):
        """
        Add a property to an entity.

        Args:
            name (str): The name of the entity in snake case.
            property_name (str): The name of the property to add.
            property_type (str): The type of the property to add.
            optional (str): Whether the property is optional.
        """
        if not ClassNameManager.is_snake_case(name):
            print("Invalid name. Must be in snake_case.")
            return
        try:
            file_path = self.entity_folder + '/' + name + '.py'
            AddPropertyCommand.modify_entity(
                file_path=file_path,
                property_name=property_name,
                property_type=property_type,
                optional=optional
            )
            print("Property added successfully.")
        except FileNotFoundError:
            print(f"Entity {name} not found")

    @staticmethod
    def modify_entity(file_path: str, property_name: str, property_type: str, optional: str):
        if not AddPropertyCommand.check_property_type(property_type):
            return
        if not AddPropertyCommand.check_optional(optional):
            return
        # Lire le contenu du fichier
        with open(file_path, 'r') as file:
            content = file.readlines()

        # Trouver la classe de l'entité et ajouter la nouvelle propriété
        class_found = False
        last_line = 0
        for i, line in enumerate(content):
            if line.strip().startswith('class ') and line.strip().endswith('(AbstractEntity, table=True):'):
                class_found = True
            if 'Field' in line:
                last_line = i
        if class_found and optional == 'no':
            content.insert(
                last_line + 1, f'    {property_name}: {property_type} = Field()\n')
        if class_found and optional == 'yes':
            content.insert(
                last_line + 1, f'    {property_name}: Optional[{property_type}] = Field()\n')

        # Écrire le contenu modifié dans le fichier
        with open(file_path, 'w') as file:
            file.writelines(content)

    @staticmethod
    def check_property_type(property_type: str):
        if property_type not in ['str', 'int', 'float', 'bool', 'list', 'tuple', 'dict', 'set']:
            print(
                "\033[91mInvalid property type. Must be one of the valid Python types.\033[0m")
            return False
        return True

    @staticmethod
    def check_optional(optional: str):
        if optional not in ['yes', 'no']:
            print(
                "\033[91mInvalid optional value type. Must be one yes or no.\033[0m")
            return False
        return True
