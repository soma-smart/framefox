from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.printer import Printer


class AddPropertyCommand(AbstractCommand):
    def __init__(self):
        super().__init__('add_property')
        self.entity_folder = r"src/entity"
        self.property_types = ['str', 'int', 'float',
                               'bool', 'list', 'tuple', 'dict', 'datetime']
        self.optional = ['yes', 'no']

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
            Printer().print_msg("Invalid name. Must be in snake_case.", theme='error')
            return
        if not ModelChecker().check_entity_and_repository(name):
            Printer().print_msg("Failed to create controller.", theme='error')
            return
        try:
            file_path = self.entity_folder + '/' + name + '.py'
            self.modify_entity(
                file_path=file_path,
                property_name=property_name,
                property_type=property_type,
                optional=optional
            )
            Printer().print_msg("Property added successfully.", theme='success')
        except FileNotFoundError:
            Printer().print_msg("Entity not found.", theme='error')

    def modify_entity(self, file_path: str, property_name: str, property_type: str, optional: str):
        if not self.check_property_type(property_type):
            return
        if not AddPropertyCommand.check_optional(optional):
            return

        input_length = None
        if property_type == 'str':
            input_length = InputManager.wait_input(
                input_type='str_length',
                default=32
            )

        with open(file_path, 'r') as file:
            content = file.readlines()

        class_found = False
        last_line = 0
        for i, line in enumerate(content):
            if line.strip().startswith('class ') and line.strip().endswith('(AbstractEntity, table=True):'):
                class_found = True
            if 'Field' in line:
                last_line = i
        if class_found:
            AddPropertyCommand.insert_field(
                content=content,
                last_line=last_line,
                property_name=property_name,
                property_type=property_type,
                optional=optional,
                str_length=input_length
            )

        with open(file_path, 'w') as file:
            file.writelines(content)

    def check_property_type(self, property_type: str):
        if property_type not in self.property_types:
            Printer().print_msg(
                "Invalid property type. Must be one of the valid Python types.", theme='error'
            )
            return False
        return True

    @staticmethod
    def check_optional(optional: str):
        if optional not in ['yes', 'no']:
            Printer().print_msg(
                "Invalid optional value type. Must be one yes or no.", theme='error'
            )
            return False
        return True

    def get_choices(self, category: str):
        if category == 'property_type':
            return self.property_types
        if category == 'optional':
            return self.optional
        else:
            return None

    def get_default(self, category: str):
        if category == 'optional':
            return 'no'
        else:
            return None

    @staticmethod
    def insert_field(content, last_line, property_name, property_type, optional, str_length=None):
        if str_length:
            base_field = f'Field(max_length={str_length})'
        else:
            base_field = 'Field()'
        if optional == 'no':
            content.insert(
                last_line + 1, f'    {property_name}: {property_type} = {base_field}\n')
        else:
            content.insert(
                last_line + 1, f'    {property_name}: Optional[{property_type}] = {base_field}\n')
