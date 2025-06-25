import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager

"""
Framefox Framework - Create Feature Command
WebSocket Feature Creator for Controllers and Views
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CreateFeatureCommand(AbstractCommand):
    """
    Create WebSocket features (controllers and views only)
    Uses existing handlers from framefox/core/websocket/handlers/
    """

    def __init__(self):
        super().__init__("feature")
        self.description = "🔌 Create WebSocket features (controllers and views)"

    def execute(self):
        """Execute the feature creation wizard"""
        self._display_welcome()

        # Step 1: Feature type selection
        feature_type = self._select_feature_type()

        # Step 2: Socket type selection
        socket_type = self._select_socket_type()

        # Step 3: Get feature name
        feature_name = self._get_feature_name()

        # Step 4: Create the feature
        self._create_websocket_feature(feature_name, feature_type, socket_type)

    def _display_welcome(self):
        """Display welcome banner"""
        self.printer.print_full_text(
            "\n🦊 [bold orange1]FrameFox Feature Creator[/bold orange1]",
            linebefore=True,
        )
        self.printer.print_full_text(
            "[dim]Create WebSocket features for real-time communication[/dim]",
            newline=True,
        )

    def _select_feature_type(self) -> str:
        """Select API or Templated feature type"""
        self.printer.print_msg(
            "What type of feature do you want to create?",
            theme="bold_normal",
            linebefore=True,
        )

        self.printer.print_msg(
            "1. API - JSON-based WebSocket communication", theme="normal"
        )
        self.printer.print_msg(
            "2. Templated - Full-stack with HTML templates", theme="normal"
        )

        choice = InputManager().wait_input(
            "Feature type", choices=["1", "2"], default="2"
        )

        return "api" if choice == "1" else "templated"

    def _select_socket_type(self) -> str:
        """Select WebSocket type - Version épurée et pratique"""
        self.printer.print_msg(
            "\nQuel type de chat voulez-vous créer ?",
            theme="bold_normal",
            linebefore=True,
        )

        self.printer.print_msg(
            "1. 💬 Chat Général Simple - Un seul chat pour tout le monde",
            theme="normal",
        )
        self.printer.print_msg(
            "2. 🏠 Chat par Rooms - Plusieurs salles (general, tech, gaming...)",
            theme="normal",
        )
        self.printer.print_msg(
            "3. 🔄 Chat Complet - Général + Rooms + Private", theme="normal"
        )
        self.printer.print_msg(
            "4. 🛠️ Base Custom - Structure vide pour développement", theme="normal"
        )

        choice = InputManager().wait_input(
            "Type de chat", choices=["1", "2", "3", "4"], default="1"
        )

        socket_types = {
            "1": "general_only",
            "2": "rooms_only",
            "3": "complete",
            "4": "custom_base",
        }

        return socket_types[choice]

    def _get_feature_name(self) -> str:
        """Get and validate feature name"""
        feature_name = InputManager().wait_input(
            "Feature name (snake_case)", default="chat_feature"
        )

        if not ClassNameManager.is_snake_case(feature_name):
            self.printer.print_msg(
                "❌ Feature name must be in snake_case", theme="error"
            )
            raise Exception("Invalid feature name")

        return feature_name

    def _create_websocket_feature(
        self, feature_name: str, feature_type: str, socket_type: str
    ):
        """Create the WebSocket feature files"""
        self.printer.print_msg(
            f"\n🔧 Creating {socket_type} WebSocket feature ({feature_type})...",
            theme="bold_normal",
            linebefore=True,
        )

        # Create controller
        self._create_websocket_controller(feature_name, feature_type, socket_type)

        # Create templates (if templated)
        if feature_type == "templated":
            self._create_websocket_templates(feature_name, socket_type)

        # Success message
        self._show_success_message(feature_name, feature_type, socket_type)

    def _create_websocket_controller(
        self, feature_name: str, feature_type: str, socket_type: str
    ):
        """Create WebSocket controller using existing handlers"""
        class_name = f"{ClassNameManager.snake_to_pascal(feature_name)}Controller"

        data = {
            "feature_name": feature_name,
            "class_name": class_name,
            "feature_type": feature_type,
            "socket_type": socket_type,
        }

        controller_dir = "src/controller"
        os.makedirs(controller_dir, exist_ok=True)

        # Check if controller already exists
        file_creator = FileCreator()
        if file_creator.check_if_exists(controller_dir, f"{feature_name}_controller"):
            self.printer.print_msg(
                f"❌ Controller {feature_name} already exists!",
                theme="error",
                linebefore=True,
            )
            raise Exception("Controller already exists")

        file_path = FileCreator().create_file(
            template="feature/websocket_controller.jinja2",
            path=controller_dir,
            name=f"{feature_name}_controller",
            data=data,
        )

        self.printer.print_msg(f"✅ Controller created: {file_path}", theme="success")

    def _create_websocket_templates(self, feature_name: str, socket_type: str):
        """Create HTML templates for WebSocket feature"""
        template_dir = f"templates/{feature_name}"
        os.makedirs(template_dir, exist_ok=True)

        data = {"feature_name": feature_name, "socket_type": socket_type}

        if socket_type == "general_only":
            # ✅ Template ultra-simple
            file_path = FileCreator().create_file(
                template="feature/websocket_general_template.jinja2",
                path=template_dir,
                name="index.html",
                data=data,
                format="html",
            )
            self.printer.print_msg(
                f"✅ Simple chat template: {file_path}", theme="success"
            )

        elif socket_type == "rooms_only":
            # ✅ CORRECTION : Seulement room.html pour rooms_only
            file_path = FileCreator().create_file(
                template="feature/websocket_room_template.jinja2",
                path=template_dir,
                name="room.html",  # ✅ CORRECTION : room.html au lieu d'index.html
                data=data,
                format="html",
            )
            self.printer.print_msg(f"✅ Room template: {file_path}", theme="success")

        elif socket_type == "complete":
            # ✅ Tous les templates
            for template_name, file_name in [
                ("websocket_index_template.jinja2", "index.html"),
                ("websocket_room_template.jinja2", "room.html"),
                ("websocket_private_template.jinja2", "private.html"),
            ]:
                file_path = FileCreator().create_file(
                    template=f"feature/{template_name}",
                    path=template_dir,
                    name=file_name,
                    data=data,
                    format="html",
                )
                self.printer.print_msg(f"✅ Template: {file_path}", theme="success")

        elif socket_type == "custom_base":
            # ✅ Template minimal custom
            file_path = FileCreator().create_file(
                template="feature/websocket_custom_template.jinja2",
                path=template_dir,
                name="custom.html",
                data=data,
                format="html",
            )
            self.printer.print_msg(
                f"✅ Custom base template: {file_path}", theme="success"
            )

    def _show_success_message(
        self, feature_name: str, feature_type: str, socket_type: str
    ):
        """Show success message with usage instructions"""
        self.printer.print_full_text(
            f"\n🎉 [bold green]{feature_name} WebSocket feature created successfully![/bold green]",
            linebefore=True,
        )

        self.printer.print_msg(f"📁 Feature type: {feature_type}", theme="normal")
        self.printer.print_msg(f"🔌 Socket type: {socket_type}", theme="normal")

        # Usage instructions
        self.printer.print_full_text(
            "\n📖 [bold yellow]Usage Instructions:[/bold yellow]", linebefore=True
        )

        if socket_type == "private":
            self.printer.print_msg(
                "• Private chat: ws://localhost:8000/ws/private/{user_id}", theme="dim"
            )
        elif socket_type == "room":
            self.printer.print_msg(
                "• Room chat: ws://localhost:8000/ws/room/{room_name}", theme="dim"
            )
        elif socket_type == "both":
            self.printer.print_msg(
                "• Private chat: ws://localhost:8000/ws/private/{user_id}", theme="dim"
            )
            self.printer.print_msg(
                "• Room chat: ws://localhost:8000/ws/room/{room_name}", theme="dim"
            )
        elif socket_type == "custom":
            self.printer.print_msg(
                "• Custom socket: ws://localhost:8000/ws/custom", theme="dim"
            )

        if feature_type == "templated":
            self.printer.print_msg(
                f"• Web interface: http://localhost:8000/{feature_name}", theme="dim"
            )

        self.printer.print_full_text(
            "\n🚀 [bold cyan]Run 'framefox run' to test your WebSocket feature![/bold cyan]"
        )
