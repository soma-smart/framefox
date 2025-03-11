import importlib
import inspect
import os
import pkgutil
from pathlib import Path
from typing import Dict, List


class CommandRegistry:
    """
    Registre global de toutes les commandes disponibles.

    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandRegistry, cls).__new__(cls)
            cls._instance.commands = {}  # namespace:name -> command_class
            cls._instance.initialized = False
        return cls._instance

    def get_command(self, name: str):
        """Récupère une commande par son nom complet (ex: 'server:start')"""
        if not self.initialized:
            self.discover_commands()

        return self.commands.get(name)

    def add_command(self, command_class, namespace=None, name=None):
        """Ajoute une commande au registre avec un namespace optionnel"""
        if not name:
            class_name = command_class.__name__
            # Supprimer le suffixe 'Command'
            if class_name.endswith("Command"):
                class_name = class_name[:-7]

            # Si le namespace est un préfixe du nom de la classe, le supprimer proprement
            if namespace and class_name.lower().startswith(namespace.lower()):
                # Par exemple, pour ServerStartCommand avec namespace=server, donne Start
                class_name = class_name[len(namespace.title()) :]

            # Convertir en kebab-case
            name = ""
            for i, c in enumerate(class_name):
                if c.isupper() and i > 0:
                    name += "-" + c.lower()
                else:
                    name += c.lower()

        if not namespace:
            # Déduire namespace du module
            module_parts = command_class.__module__.split(".")
            if len(module_parts) >= 3 and module_parts[-3] == "commands":
                namespace = module_parts[-2]
            else:
                namespace = "main"

        # Créer l'identifiant de commande
        command_id = f"{namespace}:{name}" if namespace != "main" else name
        # print(
        #     f"Enregistrement de la commande: {command_id} pour classe {command_class.__name__}")
        self.commands[command_id] = command_class
        return command_id

    def discover_commands(self):
        """Découvre automatiquement toutes les commandes dans le projet"""
        if self.initialized:
            return

        # Vérifier si le projet est déjà initialisé
        project_exists = os.path.exists("src")

        # Si le projet n'existe pas, ne découvrir que la commande init
        if not project_exists:
            # Charger uniquement la commande init
            try:
                module = importlib.import_module(
                    "framefox.terminal.commands.init_command"
                )
                command_class = getattr(module, "InitCommand")
                self.add_command(command_class)
                self.initialized = True
                return
            except (ImportError, AttributeError) as e:
                print(f"Erreur lors du chargement de la commande d'initialisation: {e}")
                # Continuer avec la découverte normale si la commande init n'est pas trouvée

        # Parcourir les modules dans framefox/terminal/commands
        commands_path = Path(__file__).parent / "commands"
        self._discover_in_path(
            commands_path,
            "framefox.terminal.commands",
            excluded_commands=["InitCommand"] if project_exists else [],
        )

        # Si un dossier src/commands existe, le parcourir aussi
        src_commands = Path(__file__).parent.parent.parent / "src" / "commands"
        if src_commands.exists():
            self._discover_in_path(
                src_commands,
                "src.commands",
                excluded_commands=["InitCommand"] if project_exists else [],
            )

        self.initialized = True

    def _discover_in_path(
        self, path: Path, package_prefix: str, excluded_commands=None
    ):
        """
        Découvre les commandes dans un chemin spécifique

        Args:
            path: Chemin à explorer
            package_prefix: Préfixe du package pour l'import
            excluded_commands: Liste des noms de classes de commandes à exclure
        """
        if not path.exists():
            return

        # Initialiser la liste d'exclusion si elle est None
        excluded_commands = excluded_commands or []

        # Parcourir les sous-dossiers
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                # C'est un namespace potentiel (server, cache, etc.)
                namespace = item.name
                # Parcourir les fichiers de commande dans ce namespace
                self._discover_in_package(
                    f"{package_prefix}.{namespace}", namespace, excluded_commands
                )

        # Parcourir les commandes à la racine
        self._discover_in_package(package_prefix, "main", excluded_commands)

    def _discover_in_package(
        self, package_name: str, namespace: str, excluded_commands=None
    ):
        """Découvre les commandes dans un package Python"""
        excluded_commands = excluded_commands or []

        try:
            package = importlib.import_module(package_name)
        except ImportError:
            print(f"Package {package_name} non trouvé")
            return

        for _, name, is_pkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            if not is_pkg and name.endswith("_command"):
                try:
                    module = importlib.import_module(name)
                    for item_name in dir(module):
                        if (
                            item_name.endswith("Command")
                            and item_name != "AbstractCommand"
                        ):
                            # Vérifier si la classe doit être exclue
                            if item_name in excluded_commands:
                                continue

                            command_class = getattr(module, item_name)
                            if inspect.isclass(command_class):
                                self.add_command(command_class, namespace)
                except ImportError as e:
                    print(f"Erreur lors du chargement de {name}: {e}")

    def list_commands(self) -> Dict[str, List[str]]:
        """Retourne les commandes organisées par namespace"""
        if not self.initialized:
            self.discover_commands()

        result = {}
        for command_id in sorted(self.commands.keys()):
            if ":" in command_id:
                namespace, name = command_id.split(":", 1)
            else:
                namespace, name = "main", command_id

            if namespace not in result:
                result[namespace] = []
            result[namespace].append(name)

        return result
