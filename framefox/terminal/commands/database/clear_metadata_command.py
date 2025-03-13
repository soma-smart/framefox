import importlib
import sys

from framefox.terminal.commands.database.abstract_database_command import AbstractDatabaseCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël 
Github: https://github.com/Vasulvius
"""


class ClearMetadataCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("clear-metadata")

    def execute(self):
        """Nettoie les métadonnées SQLAlchemy et le cache Python pour résoudre les problèmes de mapper"""
        try:
            self.printer.print_msg(
                "Nettoyage des métadonnées SQLAlchemy...", theme="info")

            # 2. Réinitialiser les registres et mappers SQLAlchemy
            self.clear_sqlalchemy_registry()

            self.printer.print_msg(
                "Métadonnées nettoyées avec succès", theme="success")
            self.printer.print_msg(
                "Redémarrez votre application pour appliquer les changements", theme="info")

        except Exception as e:
            self.printer.print_msg(
                f"Erreur lors du nettoyage des métadonnées : {str(e)}",
                theme="error",
            )

    def clear_sqlalchemy_registry(self):
        """Réinitialise le registre SQLAlchemy"""
        try:
            # Importer les modules nécessaires
            from sqlalchemy import inspect
            from sqlmodel import SQLModel
            from sqlalchemy.orm import clear_mappers

            # Nettoyer les mappers SQLAlchemy
            clear_mappers()

            # Réinitialiser le registry de SQLModel de façon alternative
            try:
                # Méthode 1: Si c'est une version récente avec SQLModel.metadata
                if hasattr(SQLModel, 'metadata'):
                    SQLModel.metadata.clear()
                    self.printer.print_msg(
                        "SQLModel.metadata nettoyé", theme="info")

                # Méthode 2: Accès aux classes internes de SQLModel
                if hasattr(SQLModel, '__class__') and hasattr(SQLModel.__class__, 'registry'):
                    SQLModel.__class__.registry.dispose()
                    self.printer.print_msg(
                        "SQLModel registry nettoyé", theme="info")
            except Exception as inner_e:
                self.printer.print_msg(
                    f"Nettoyage partiel de SQLModel: {str(inner_e)}", theme="warning")

            # Alternative simplifiée: recharger complètement le module SQLModel
            if 'sqlmodel' in sys.modules:
                importlib.reload(sys.modules['sqlmodel'])
                self.printer.print_msg(
                    "Module SQLModel rechargé", theme="info")

            # Recharger les modules importants
            modules_to_reload = [
                'framefox.core.orm.abstract_entity',
                'src.entity',
                'sqlalchemy.orm.mapper'
            ]

            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])

            # Nettoyer les modules d'entité spécifiques
            entity_modules = [
                m for m in sys.modules if m.startswith('src.entity.')]
            for module_name in entity_modules:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])

            self.printer.print_msg(
                "Registres SQLAlchemy réinitialisés", theme="info")

        except ImportError as e:
            self.printer.print_msg(
                f"Module non trouvé: {str(e)}", theme="warning")
            # Continue quand même avec le reste du processus

        except Exception as e:
            self.printer.print_msg(
                f"Erreur lors de la réinitialisation: {str(e)}", theme="warning")
            # Ne pas lever d'exception pour permettre au reste du processus de continuer
