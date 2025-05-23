"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class StaticResourceDetector:
    """
    Utility class for detecting static resources in web requests.
    Provides centralized configuration for static file extensions.
    """
    

    STATIC_EXTENSIONS = [
        '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
        '.ico', '.woff', '.woff2', '.ttf', '.eot', '.webp', '.avif',
        '.pdf', '.zip', '.mp4', '.webm', '.mp3', '.wav'
    ]
    
    @classmethod
    def is_static_resource(cls, path: str) -> bool:
        """
        Check if a given path points to a static resource.
        
        Args:
            path: The URL path to check
            
        Returns:
            True if the path ends with a static file extension
        """
        return any(path.lower().endswith(ext) for ext in cls.STATIC_EXTENSIONS)
    
    @classmethod
    def get_extensions(cls) -> list[str]:
        """
        Get the list of static file extensions.
        
        Returns:
            List of static file extensions
        """
        return cls.STATIC_EXTENSIONS.copy()