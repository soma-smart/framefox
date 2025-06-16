import os, re
from typing import Dict
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""
class EnvManager:
    """
    Manager for manipulating .env files
    """
    
    def __init__(self, env_path: str = ".env"):
        self.env_path = env_path
    
    def add_variables(self, variables: Dict[str, str], section_title: str = None) -> None:
        if not os.path.exists(self.env_path):
            with open(self.env_path, 'w') as f:
                f.write("# Environment variables\n\n")
        
        with open(self.env_path, 'r') as f:
            content = f.read()
        
        existing_vars = self._get_existing_variables(content)
        new_vars = {}
        
        for key, value in variables.items():
            if key not in existing_vars:
                new_vars[key] = value
        
        if new_vars:
            self._append_variables(new_vars, section_title)
    
    def _get_existing_variables(self, content: str) -> Dict[str, str]:
        existing = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=')[0].strip()
                value = '='.join(line.split('=')[1:]).strip()
                existing[key] = value
        return existing
    
    def _append_variables(self, variables: Dict[str, str], section_title: str = None) -> None:
        with open(self.env_path, 'a') as f:
            f.write('\n')
            
            if section_title:
                f.write(f"#==============================\n")
                f.write(f"# {section_title}\n")
                f.write(f"#==============================\n")
            
            for key, value in variables.items():
                f.write(f"{key}={value}\n")
    
    def variable_exists(self, variable_name: str) -> bool:
        if not os.path.exists(self.env_path):
            return False
            
        with open(self.env_path, 'r') as f:
            content = f.read()
            
        pattern = rf'^{re.escape(variable_name)}\s*='
        return bool(re.search(pattern, content, re.MULTILINE))
    
    def get_section_variables(self, auth_type: str) -> Dict[str, str]:
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
        titles = {
            "oauth_google": "Google OAuth Configuration",
            "oauth_microsoft": "Microsoft OAuth Configuration", 
            "jwt_api": "JWT Configuration"
        }
        return titles.get(auth_type, "Authentication Configuration")
