from pathlib import Path
import os
import hashlib
import json
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from framefox.core.di.service_container import ServiceContainer
from framefox.core.form.extension.form_extension import FormExtension

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TemplateRenderer:
    def __init__(self):
        self.container = ServiceContainer()
        self.settings = self.container.get_by_name("Settings")
        self.user_template_dir = self.settings.template_dir
        self.framework_template_dir = Path(__file__).parent / "views"
        self.public_path = self.settings.public_path if hasattr(
            self.settings, 'public_path') else 'public'
        self.env = Environment(
            loader=FileSystemLoader(
                [self.user_template_dir, str(self.framework_template_dir)]
            ),
            undefined=StrictUndefined,
        )
        form_extension = FormExtension(self.env)
        self.env.globals["url_for"] = self.url_for
        self.env.globals["get_flash_messages"] = self.get_flash_messages
        self.env.globals["current_user"] = self.get_current_user
        self.env.globals["asset"] = self.asset
        self.env.globals["dump"] = self._dump_function

        self._register_filters(self.env)

    def url_for(self, name: str, **params) -> str:
        """Generates a URL from the route name"""
        try:
            router = self.container.get_by_name("Router")
            return str(router.url_path_for(name, **params))
        except Exception as e:
            print(f"Error generating URL for route '{name}': {str(e)}")
            return "#"

    def get_flash_messages(self):
        """Retrieves flash messages from the session in template format"""
        session = self.container.get_by_name("Session")
        flash_bag = session.get_flash_bag()
        return flash_bag.get_for_template()

    def render(self, template_name: str, context: dict = {}) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

    def _register_filters(self, env):
        """Registers custom filters for Jinja2"""
        env.filters["relation_display"] = self._relation_display_filter
        env.filters["date"] = self._date_filter
        env.filters["format_date"] = self._format_date_filter
        env.filters["filesizeformat"] = self._filesize_format_filter
        env.filters["json_encode"] = self._json_encode_filter

        env.filters["split"] = self._split_filter
        env.filters["last"] = self._last_filter
        env.filters["lower"] = self._lower_filter
        env.filters["format_number"] = self._format_number_filter
        env.filters["min"] = self._min_filter
        env.filters["max"] = self._max_filter

    def _max_filter(self, value, max_value):
        """Retourne la valeur maximale entre deux nombres"""
        try:
            return max(float(value), float(max_value))
        except (ValueError, TypeError):
            return value

    def _min_filter(self, value, max_value):
        """Retourne la valeur minimale entre deux nombres"""
        try:
            return min(float(value), float(max_value))
        except (ValueError, TypeError):
            return value

    def _split_filter(self, value, delimiter=','):
        """Splits a string by a delimiter"""
        if not value:
            return []
        return value.split(delimiter)

    def _last_filter(self, value):
        """Returns the last element of a list"""
        if not value or not isinstance(value, (list, tuple)):
            return ''
        return value[-1] if value else ''

    def _lower_filter(self, value):
        """Converts a string to lowercase"""
        if value is None:
            return ''
        return str(value).lower()

    def _json_encode_filter(self, value):
        """Converts a Python value to a JSON string"""
        try:
            return json.dumps(value)
        except TypeError:
            return json.dumps(str(value))

    def _filesize_format_filter(self, size):
        """Format file size in human readable format"""
        if size is None:
            return "0 B"

        try:
            size = float(size)
        except (ValueError, TypeError):
            return str(size)

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                if unit == 'B':
                    return f"{int(size)} {unit}"
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def _relation_display_filter(self, value):
        """Filter to properly display relations"""
        if value is None:
            return "None"
        elif isinstance(value, list):
            if len(value) == 0:
                return "None"
            elif hasattr(value[0], "id") and hasattr(value[0], "name"):
                return ", ".join([item.name for item in value])
            else:
                return f"{len(value)} items"
        elif hasattr(value, "id") and hasattr(value, "name"):
            return value.name
        elif hasattr(value, "id"):
            return f"ID: {value.id}"
        else:
            return str(value)

    def _date_filter(self, value, format="%d/%m/%Y"):
        """Filter to format dates in templates"""
        if value is None:
            return ""

        if isinstance(value, str):
            try:
                from datetime import datetime
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return value

        try:
            return value.strftime(format)
        except:
            return str(value)

    def _format_date_filter(self, value, format="%d/%m/%Y %H:%M"):
        """Filter to format dates with time in templates"""
        return self._date_filter(value, format)

    def get_current_user(self):
        """Récupère l'utilisateur actuellement connecté pour les templates"""
        try:
            user_provider = self.container.get_by_name("UserProvider")
            return user_provider.get_current_user()
        except Exception as e:
            print(f"Error retrieving current user: {str(e)}")
            return None

    def asset(self, path: str, versioning: bool = True) -> str:
        """
        Generates a URL for a static resource

        Args:
            path: Relative path of the file in the public folder
            versioning: Enables versioning for cache invalidation

        Returns:
            Full URL to the resource
        """
        path = path.lstrip('/')
        base_url = self.settings.base_url if hasattr(
            self.settings, 'base_url') else ''
        asset_url = f"{base_url}/{path}"

        if versioning:
            file_path = os.path.join(self.public_path, path)
            if os.path.exists(file_path):
                timestamp = os.path.getmtime(file_path)
                version = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
                asset_url += f"?v={version}"
            else:
                import time
                asset_url += f"?v={int(time.time())}"

        return asset_url

    def _dump_function(self, obj):
        """Function to display the content of an object in templates"""
        import pprint
        return pprint.pformat(obj, depth=3)

    def _format_number_filter(self, value, decimal_places=2, decimal_separator=',', thousand_separator=' '):
        """
        Formats a number with thousand separators and decimals.

        Args:
            value: The number to format
            decimal_places: Number of decimal places to display
            decimal_separator: Character for decimal separator
            thousand_separator: Character for thousand separator

        Usage: 
            {{ 1234.5678|format_number }}           -> 1 234,57
            {{ 1234.5678|format_number(1) }}        -> 1 234,6
            {{ 1234.5678|format_number(3, '.') }}   -> 1 234.568
            {{ 1234.5678|format_number(0, ',', '.') }} -> 1.235
        """
        if value is None:
            return "0"

        try:
            value = float(value)
        except (ValueError, TypeError):
            return str(value)

        format_string = "{:,.%df}" % decimal_places
        formatted = format_string.format(value)

        if thousand_separator != ',' or decimal_separator != '.':
            parts = formatted.split('.')
            if len(parts) == 2:
                formatted = thousand_separator.join(
                    parts[0].split(',')
                ) + decimal_separator + parts[1]
            else:
                formatted = thousand_separator.join(formatted.split(','))

        return formatted
