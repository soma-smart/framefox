import os
import re
from typing import Dict, List

class EnvManager:
    """
    Gestionnaire pour manipuler le fichier .env
    """
    
    def __init__(self, env_path: str = ".env"):
        self.env_path = env_path
    
    def add_variables(self, variables: Dict[str, str], section_title: str = None) -> None:
        """
        Ajoute des variables au fichier .env
        
        Args:
            variables: Dictionnaire {clé: valeur} des variables à ajouter
            section_title: Titre de la section (optionnel)
        """
        # Créer le fichier s'il n'existe pas
        if not os.path.exists(self.env_path):
            with open(self.env_path, 'w') as f:
                f.write("# Environment variables\n\n")
        
        # Lire le contenu existant
        with open(self.env_path, 'r') as f:
            content = f.read()
        
        # Vérifier quelles variables existent déjà
        existing_vars = self._get_existing_variables(content)
        new_vars = {}
        
        for key, value in variables.items():
            if key not in existing_vars:
                new_vars[key] = value
        
        # Ajouter seulement les nouvelles variables
        if new_vars:
            self._append_variables(new_vars, section_title)
    
    def _get_existing_variables(self, content: str) -> Dict[str, str]:
        """
        Extrait les variables existantes du contenu .env
        
        Returns:
            Dictionnaire des variables existantes
        """
        existing = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                value = '='.join(line.split('=')[1:]).strip()
                existing[key] = value
        return existing
    
    def _append_variables(self, variables: Dict[str, str], section_title: str = None) -> None:
        """
        Ajoute les variables à la fin du fichier .env
        """
        with open(self.env_path, 'a') as f:
            # Ajouter une ligne vide avant la nouvelle section
            f.write('\n')
            
            # Ajouter le titre de section si fourni
            if section_title:
                f.write(f"#==============================\n")
                f.write(f"# {section_title}\n")
                f.write(f"#==============================\n")
            
            # Ajouter les variables
            for key, value in variables.items():
                f.write(f"{key}={value}\n")
    
    def variable_exists(self, variable_name: str) -> bool:
        """
        Vérifie si une variable existe dans le .env
        
        Args:
            variable_name: Nom de la variable à vérifier
            
        Returns:
            True si la variable existe, False sinon
        """
        if not os.path.exists(self.env_path):
            return False
            
        with open(self.env_path, 'r') as f:
            content = f.read()
            
        pattern = rf'^{re.escape(variable_name)}\s*='
        return bool(re.search(pattern, content, re.MULTILINE))
    
    def get_section_variables(self, auth_type: str) -> Dict[str, str]:
        """
        Retourne les variables d'environnement nécessaires selon le type d'auth
        
        Args:
            auth_type: Type d'authentification (oauth_google, oauth_microsoft, jwt_api)
            
        Returns:
            Dictionnaire des variables nécessaires
        """
        if auth_type == "oauth_google":
            return {
                "GOOGLE_CLIENT_ID": "your_google_client_id",
                "GOOGLE_CLIENT_SECRET": "your_google_client_secret",
                "APP_URL": "http://localhost:8000"
            }
        elif auth_type == "oauth_microsoft":
            return {
                "MICROSOFT_CLIENT_ID": "your_microsoft_client_id", 
                "MICROSOFT_CLIENT_SECRET": "your_microsoft_client_secret",
                "MICROSOFT_TENANT_ID": "your_microsoft_tenant_id",
                "APP_URL": "http://localhost:8000"
            }
        elif auth_type == "jwt_api":
            return {
                "JWT_SECRET_KEY": "your-super-secret-jwt-key-change-this-in-production"
            }
        else:
            return {}
    
    def get_section_title(self, auth_type: str) -> str:
        """
        Retourne le titre de section pour le type d'auth
        """
        titles = {
            "oauth_google": "Google OAuth Configuration",
            "oauth_microsoft": "Microsoft OAuth Configuration", 
            "jwt_api": "JWT Configuration"
        }
        return titles.get(auth_type, "Authentication Configuration")