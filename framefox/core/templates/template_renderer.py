import hashlib
import json
import logging
import os
import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError, UndefinedError

from framefox.core.di.service_container import ServiceContainer
from framefox.core.form.extension.form_extension import FormExtension
from framefox.core.request.request_stack import RequestStack

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
        self.logger = logging.getLogger("TEMPLATE_RENDERER")
        self.settings = self.container.get_by_name("Settings")

        self.user_template_dir = self.settings.template_dir
        self.framework_template_dir = Path(__file__).parent / "views"
        self.public_path = getattr(self.settings, "public_path", "public")

        self._setup_jinja_environment()
        self._register_filters()
        self._register_globals()

    def _setup_jinja_environment(self):
        self.env = Environment(
            loader=FileSystemLoader([self.user_template_dir, str(self.framework_template_dir)]),
            undefined=StrictUndefined,
        )

        FormExtension(self.env)

    def _register_globals(self):
        globals_map = {
            "url_for": self.url_for,
            "get_flash_messages": self.get_flash_messages,
            "current_user": self.get_current_user,
            "asset": self.asset,
            "dump": self._dump_function,
            "request": self.get_current_request,
            "csrf_token": self.get_csrf_token,
        }

        for name, func in globals_map.items():
            self.env.globals[name] = func

    def _register_filters(self):
        filters_map = {
            "relation_display": self._relation_display_filter,
            "date": self._date_filter,
            "format_date": self._format_date_filter,
            "time": self._time_filter,
            "filesizeformat": self._filesize_format_filter,
            "format_number": self._format_number_filter,
            "min": self._min_filter,
            "max": self._max_filter,
            "split": self._split_filter,
            "last": self._last_filter,
            "lower": self._lower_filter,
            "slice": self._slice_filter,
            "json_encode": self._json_encode_filter,
        }

        for name, filter_func in filters_map.items():
            self.env.filters[name] = filter_func

    def render(self, template_name: str, context: dict = None) -> str:
        if context is None:
            context = {}

        if "request" not in context:
            request = self.get_current_request()
            if request:
                context["request"] = request

        memory_collector = self._start_template_profiling(template_name)
        start_time = time.time()

        try:
            template = self.env.get_template(template_name)
            result = template.render(**context)

            self._end_template_profiling(memory_collector, template_name, start_time)

            return result

        except (TemplateNotFound, TemplateSyntaxError, UndefinedError):
            if memory_collector and hasattr(memory_collector, "end_template_measurement"):
                memory_collector.end_template_measurement()

            self.logger.error(f"Template error in {template_name}")
            raise

        except Exception as e:
            if memory_collector and hasattr(memory_collector, "end_template_measurement"):
                memory_collector.end_template_measurement()

            self.logger.error(f"Unexpected template rendering error in {template_name}: {str(e)}")
            raise

    def _start_template_profiling(self, template_name: str):
        try:
            from framefox.core.debug.profiler.profiler import Profiler

            profiler = Profiler()
            if profiler.is_enabled():
                memory_collector = profiler.get_collector("memory")
                if memory_collector and hasattr(memory_collector, "start_template_measurement"):
                    memory_collector.start_template_measurement()
                    return memory_collector
        except Exception:
            pass
        return None

    def _end_template_profiling(self, memory_collector, template_name: str, start_time: float):
        if not memory_collector:
            return

        try:
            end_time = time.time()
            render_time_ms = (end_time - start_time) * 1000

            if hasattr(memory_collector, "end_template_measurement"):
                template_memory = memory_collector.end_template_measurement()

                if hasattr(memory_collector, "add_template_metrics"):
                    memory_collector.add_template_metrics(template_memory, render_time_ms)
        except Exception:
            pass

    def get_csrf_token(self) -> str:
        try:
            session = self.container.get_by_name("Session")
            csrf_manager = self.container.get_by_name("CsrfTokenManager")

            csrf_token = csrf_manager.generate_token()
            session.set("csrf_token", csrf_token)
            session.save()

            return csrf_token
        except Exception as e:
            self.logger.error(f"Error generating CSRF token: {e}")
            return ""

    def url_for(self, name: str, **params) -> str:
        try:
            router = self.container.get_by_name("Router")
            return str(router.url_path_for(name, **params))
        except Exception as e:
            self.logger.error(f"Error generating URL for route '{name}': {str(e)}")
            return "#"

    def get_current_request(self):
        try:
            return RequestStack.get_request()
        except Exception:
            return None

    def get_flash_messages(self):
        try:
            session = self.container.get_by_name("Session")
            flash_bag = session.get_flash_bag()
            return flash_bag.get_for_template()
        except Exception as e:
            self.logger.error(f"Error retrieving flash messages: {e}")
            return {}

    def get_current_user(self):
        try:
            user_provider = self.container.get_by_name("UserProvider")
            return user_provider.get_current_user()
        except Exception:
            return None

    def asset(self, path: str, versioning: bool = True) -> str:
        path = path.lstrip("/")
        base_url = getattr(self.settings, "base_url", "")
        asset_url = f"{base_url}/{path}"

        if versioning:
            file_path = os.path.join(self.public_path, path)
            if os.path.exists(file_path):
                timestamp = os.path.getmtime(file_path)
                version = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
                asset_url += f"?v={version}"
            else:
                asset_url += f"?v={int(time.time())}"

        return asset_url

    def _dump_function(self, obj):
        import pprint

        return pprint.pformat(obj, depth=3)

    def _relation_display_filter(self, value):
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
        if value is None:
            return ""

        if isinstance(value, (int, float)):
            try:
                from datetime import datetime

                value = datetime.fromtimestamp(value)
            except (ValueError, TypeError, OverflowError):
                return str(value)

        if isinstance(value, str):
            try:
                from datetime import datetime

                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return value

        try:
            return value.strftime(format)
        except Exception:
            return str(value)

    def _format_date_filter(self, value, format="%d/%m/%Y %H:%M"):
        return self._date_filter(value, format)

    def _time_filter(self, value, include_ms=True):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return str(value) + " ms"

        seconds, milliseconds = divmod(value, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            if include_ms:
                return f"{int(hours)}h {int(minutes)}min {int(seconds)}s {int(milliseconds)}ms"
            return f"{int(hours)}h {int(minutes)}min {int(seconds)}s"
        elif minutes > 0:
            if include_ms:
                return f"{int(minutes)}min {int(seconds)}s {int(milliseconds)}ms"
            return f"{int(minutes)}min {int(seconds)}s"
        elif seconds > 0:
            if include_ms:
                return f"{int(seconds)}s {int(milliseconds)}ms"
            return f"{int(seconds)}s"
        else:
            return f"{int(milliseconds)} ms"

    def _filesize_format_filter(self, size):
        if size is None:
            return "0 B"

        try:
            size = float(size)
        except (ValueError, TypeError):
            return str(size)

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                if unit == "B":
                    return f"{int(size)} {unit}"
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def _format_number_filter(self, value, decimal_places=2, decimal_separator=",", thousand_separator=" "):
        if value is None:
            return "0"

        try:
            value = float(value)
        except (ValueError, TypeError):
            return str(value)

        format_string = "{:,.%df}" % decimal_places
        formatted = format_string.format(value)

        if thousand_separator != "," or decimal_separator != ".":
            parts = formatted.split(".")
            if len(parts) == 2:
                formatted = thousand_separator.join(parts[0].split(",")) + decimal_separator + parts[1]
            else:
                formatted = thousand_separator.join(formatted.split(","))

        return formatted

    def _min_filter(self, value, min_value=None):
        try:
            if min_value is None:
                if isinstance(value, (list, tuple)) and value:
                    return min(value)
                return value
            else:
                return min(float(value), float(min_value))
        except (ValueError, TypeError):
            return value

    def _max_filter(self, value, max_value=None):
        try:
            if max_value is None:
                if isinstance(value, (list, tuple)) and value:
                    return max(value)
                return value
            else:
                return max(float(value), float(max_value))
        except (ValueError, TypeError):
            return value

    def _split_filter(self, value, delimiter=","):
        if not value:
            return []
        return str(value).split(delimiter)

    def _last_filter(self, value):
        if not value or not isinstance(value, (list, tuple)):
            return ""
        return value[-1] if value else ""

    def _lower_filter(self, value):
        if value is None:
            return ""
        return str(value).lower()

    def _slice_filter(self, value, start, length=None):
        try:
            if length:
                return str(value)[start : start + length]
            return str(value)[start:]
        except (ValueError, TypeError):
            return value

    def _json_encode_filter(self, value):
        try:
            return json.dumps(value)
        except TypeError:
            return json.dumps(str(value))
