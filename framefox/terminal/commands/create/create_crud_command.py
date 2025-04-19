import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class CreateCrudCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        self.api_controller_template = r"api_crud_controller_template.jinja2"
        self.templated_controller_template = (
            r"templated_crud_controller_template.jinja2"
        )
        self.controllers_path = r"src/controllers"
        self.input_choices = ["api", "templated"]
        self.templates_path = r"templates"

    def _create_view_templates(self, entity_name: str):
        template_dir = os.path.join(self.templates_path, entity_name)
        os.makedirs(template_dir, exist_ok=True)
        properties = ModelChecker().get_entity_properties(entity_name)

        templates = {
            "create": "create_template.jinja2",
            "read": "read_template.jinja2",
            "update": "update_template.jinja2",
            "index": "read_all_template.jinja2",
        }

        data = {"entity_name": entity_name, "properties": properties}

        file_creator = FileCreator()
        for output_name, template_file in templates.items():
            file_creator.create_file(
                template=f"crud/{template_file}",
                path=template_dir,
                name=output_name + ".html",
                data=data,
                format="html",
            )

    def execute(self, entity_name: str = None):
        self.printer.print_msg(
            "What is the name of the entity you want to create a CRUD with ?(snake_case)",
            theme="bold_normal",
            linebefore=True,
        )
        if entity_name is None:
            entity_name = InputManager().wait_input("Entity name")
            if entity_name == "":
                return

        if not ClassNameManager.is_snake_case(entity_name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        if not ModelChecker().check_entity_and_repository(entity_name):
            self.printer.print_msg(
                "Failed to create controller. Entity or repository does not exist.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        self.printer.print_msg(
            "What type of controller do you want to create?",
            theme="bold_normal",
            linebefore=True,
        )

        print("")

        self.printer.print_msg(
            "1.[bold orange1]API CRUD controller[/bold orange1]",
            theme="normal",
        )
        self.printer.print_msg(
            "2.[bold orange1]Templated CRUD controller[/bold orange1]",
            theme="normal",
            newline=True,
        )

        user_choice = InputManager().wait_input(
            "CRUD controller type", choices=["1", "2"], default="1"
        )

        user_input = "templated" if user_choice == "2" else "api"
        entity_class_name = ClassNameManager.snake_to_pascal(entity_name)
        class_name = f"{entity_class_name}Controller"
        data = {
            "controller_class_name": class_name,
            "repository_file_name": f"{entity_name}_repository",
            "repository_class_name": f"{entity_class_name}Repository",
            "entity_file_name": entity_name,
            "entity_class_name": entity_class_name,
            "entity_name": entity_name,
        }

        file_creator = FileCreator()
        if file_creator.check_if_exists(
            self.controllers_path, f"{entity_name}_controller"
        ):
            self.printer.print_msg(
                f"Controller {entity_name} already exists!",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        if user_input == "api":
            file_path = FileCreator().create_file(
                self.api_controller_template,
                self.controllers_path,
                f"{entity_name}_controller",
                data,
            )

        if user_input == "templated":

            file_path = FileCreator().create_file(
                self.templated_controller_template,
                self.controllers_path,
                f"{entity_name}_controller",
                data,
            )
            # Créer le FormType pour l'entité
            self._create_form_type(entity_name)
            self._create_view_templates(entity_name)

        self.printer.print_msg(
            f"✓ CRUD Controller created successfully: {file_path}",
            theme="success",
            linebefore=True,
        )

    def _create_form_type(self, entity_name: str):
        """Génère un FormType pour l'entité spécifiée."""
        # Récupérer les propriétés de l'entité
        properties = ModelChecker().get_entity_properties(entity_name)
        entity_class_name = ClassNameManager.snake_to_pascal(entity_name)

        # Préparer les données pour le template
        data = {
            "entity_name": entity_name,
            "entity_class_name": entity_class_name,
            "form_type_class_name": f"{entity_class_name}Type",
            "properties": properties,
        }

        # Créer le répertoire des formulaires si nécessaire
        form_types_dir = "src/form"
        os.makedirs(form_types_dir, exist_ok=True)

        # Générer le fichier FormType
        file_creator = FileCreator()
        file_path = file_creator.create_file(
            template="form/form_type_template.jinja2",
            path=form_types_dir,
            name=f"{entity_name}_type",
            data=data,
            format="py",
        )

        self.printer.print_msg(
            f"✓ Form type created successfully: {file_path}", theme="success"
        )

        return file_path
