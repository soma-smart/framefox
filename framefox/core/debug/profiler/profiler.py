import datetime
import json
import logging
import os
import random
import shutil
import time
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from fastapi import Request, Response

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class DataCollector:
    def __init__(self, name: str, icon: str):
        self.name = name
        self.icon = icon
        self.data = {}

    def collect(self, request: Request, response: Response) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        return self.data


class LogDataCollector(DataCollector):
    def __init__(self):
        super().__init__("log", "fa-list")
        self.records = []
        self._setup_handler()

    def _setup_handler(self):
        class ProfilerLogHandler(logging.Handler):
            def __init__(self, collector):
                super().__init__()
                self.collector = collector

            def emit(self, record):
                self.collector.add_record(record)

        self.handler = ProfilerLogHandler(self)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.handler)

    def add_record(self, record):
        self.records.append(
            {
                "message": record.getMessage(),
                "level": record.levelname,
                "channel": record.name,
                "timestamp": record.created,
                "context": getattr(record, "context", {}),
            }
        )

    def collect(self, request: Request, response: Response) -> None:
        self.data = {
            "records": self.records,
            "count": len(self.records),
            "error_count": sum(1 for r in self.records if r["level"] in ("ERROR", "CRITICAL")),
        }


class ExceptionDataCollector(DataCollector):
    def __init__(self):
        super().__init__("exception", "fa-bug")
        self.exception = None

    def collect_exception(self, exception: Exception, stack_trace: str = None) -> None:
        self.exception = {
            "class": exception.__class__.__name__,
            "message": str(exception),
            "code": getattr(exception, "code", 0),
            "trace": stack_trace or traceback.format_exc(),
            "file": self._get_exception_file(exception),
            "line": self._get_exception_line(exception),
        }

    def _get_exception_file(self, exception):
        if hasattr(exception, "__traceback__") and exception.__traceback__:
            return exception.__traceback__.tb_frame.f_code.co_filename
        return "Unknown"

    def _get_exception_line(self, exception):
        if hasattr(exception, "__traceback__") and exception.__traceback__:
            return exception.__traceback__.tb_lineno
        return 0

    def collect(self, request: Request, response: Response) -> None:
        if hasattr(request.state, "exception"):
            self.exception = request.state.exception

        self.data = {
            "exception": self.exception,
            "status_code": (response.status_code if hasattr(response, "status_code") else 500),
            "has_exception": self.exception is not None,
        }


class RequestDataCollector(DataCollector):
    def __init__(self):
        super().__init__("request", "fa-globe")

    def collect(self, request: Request, response: Response) -> None:
        self.data = {
            "method": request.method,
            "path": request.url.path,
            "path_params": dict(request.path_params),
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else "unknown",
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
        }


class TimeDataCollector(DataCollector):
    def __init__(self):
        super().__init__("time", "fa-clock")

    def collect(self, request: Request, response: Response) -> None:
        end_time = time.time()
        start_time = getattr(request.state, "request_start_time", None)

        if start_time is None:
            request_duration = getattr(request.state, "request_duration", None)
            if request_duration:
                start_time = end_time - (request_duration / 1000)
            else:
                start_time = end_time - 0.01

        self.data = {
            "start_time": start_time,
            "end_time": end_time,
            "duration": round((end_time - start_time) * 1000, 2),
        }


class MemoryDataCollector(DataCollector):
    def __init__(self):
        super().__init__("memory", "fa-memory")

    def collect(self, request: Request, response: Response) -> None:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        self.data = {
            "memory_usage": memory_info.rss / (1024 * 1024),
            "peak_memory": memory_info.vms / (1024 * 1024),
        }


class SQLDataCollector(DataCollector):
    def __init__(self):
        super().__init__("database", "fa-database")
        self.queries = []

    def add_query(self, query: str, parameters: Dict, duration: float) -> None:
        self.queries.append({"query": query, "parameters": parameters, "duration": duration})

    def collect(self, request: Request, response: Response) -> None:
        self.data = {
            "queries": self.queries,
            "query_count": len(self.queries),
            "total_duration": sum(q["duration"] for q in self.queries),
        }


class RouteDataCollector(DataCollector):
    def __init__(self):
        super().__init__("route", "fa-map-signs")

    def collect(self, request: Request, response: Response) -> None:
        from framefox.core.routing.router import Router

        endpoint = request.scope.get("endpoint", None)
        path = request.url.path
        route_name = "unknown"
        controller_name = "unknown"
        method_name = "unknown"
        allowed_methods = []
        template = None

        if endpoint:
            full_name = getattr(endpoint, "__qualname__", str(endpoint))
            if "." in full_name:
                parts = full_name.split(".", 1)
                controller_name = parts[0]
                method_name = parts[1]
            else:
                method_name = full_name

            module_name = getattr(endpoint, "__module__", "")
            if module_name and controller_name != "unknown":
                controller_name = f"{module_name}.{controller_name}"

            if hasattr(endpoint, "route_info"):
                route_info = getattr(endpoint, "route_info")
                if isinstance(route_info, dict) and "methods" in route_info:
                    allowed_methods = route_info.get("methods", [])

            for name, route_path in Router._routes.items():
                route_parts = route_path.split("/")
                path_parts = path.split("/")

                if len(route_parts) == len(path_parts):
                    match = True
                    for i, (route_part, path_part) in enumerate(zip(route_parts, path_parts)):
                        if route_part and route_part[0] == "{" and route_part[-1] == "}":
                            continue
                        if route_part != path_part:
                            match = False
                            break

                    if match:
                        route_name = name
                        break
            if hasattr(response, "template_name"):
                template = response.template_name

            elif hasattr(request.state, "template"):
                template = request.state.template
            elif hasattr(endpoint, "__self__"):
                controller_instance = getattr(endpoint, "__self__")
                if hasattr(controller_instance, "_last_rendered_template"):
                    template = controller_instance._last_rendered_template

        self.data = {
            "route": path,
            "route_name": route_name,
            "endpoint": str(endpoint),
            "controller_name": controller_name,
            "method_name": method_name,
            "allowed_methods": allowed_methods,
            "template": template,
        }


class Profiler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Profiler, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.collectors = {}
        self.profiles_cache = {}
        self.enabled = False
        self.max_profiles_in_memory = 50
        self.max_profiles_per_day = 1000
        self.retention_days = 7
        self.sampling_rate = 1.0
        self.exclude_paths = [
            "/static",
            "/_profiler",
            "/favicon.ico",
        ]

        self.base_storage_dir = Path("var/profiler")

        self.logger = logging.getLogger("PROFILER")
        self.register_collector(RequestDataCollector())
        self.register_collector(TimeDataCollector())
        self.register_collector(MemoryDataCollector())
        self.register_collector(SQLDataCollector())
        self.register_collector(RouteDataCollector())
        self.register_collector(ExceptionDataCollector())
        self.register_collector(LogDataCollector())

        self._setup_storage_directory()
        self._cleanup_old_profiles()
        self.initialized = True

    def _setup_storage_directory(self) -> None:
        today = self._get_today_folder()
        self.storage_dir = self.base_storage_dir / today
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._check_daily_profile_limit()

    def _get_today_folder(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _check_daily_profile_limit(self) -> None:
        if not self.storage_dir.exists():
            return

        profile_count = len(list(self.storage_dir.glob("*.json")))
        if profile_count >= self.max_profiles_per_day:
            self.logger.warning(f"Maximum number of profiles reached for today ({profile_count}). Replacing oldest profiles.")

    def _cleanup_old_profiles(self) -> None:
        try:
            if not self.base_storage_dir.exists():
                return

            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")

            for date_dir in self.base_storage_dir.iterdir():
                if date_dir.is_dir() and date_dir.name < cutoff_str:
                    self.logger.info(f"Cleaning up old profiles in {date_dir}")
                    shutil.rmtree(date_dir)
        except Exception as e:
            self.logger.error(f"Error cleaning up old profiles: {str(e)}")

    def _maintain_cache_size(self) -> None:
        if len(self.profiles_cache) > self.max_profiles_in_memory:
            sorted_keys = sorted(self.profiles_cache.keys())
            keys_to_remove = sorted_keys[: -self.max_profiles_in_memory]
            for key in keys_to_remove:
                self.profiles_cache.pop(key, None)

    def _find_oldest_profile(self) -> Optional[Path]:
        if not self.storage_dir.exists():
            return None

        files = list(self.storage_dir.glob("*.json"))
        if not files:
            return None

        return min(files, key=lambda p: p.stat().st_mtime)

    def enable(self) -> None:
        self.enabled = True
        self._setup_storage_directory()

    def disable(self) -> None:
        self.enabled = False

    def is_enabled(self) -> bool:
        return self.enabled

    def register_collector(self, collector: DataCollector) -> None:
        self.collectors[collector.name] = collector

    def get_collector(self, name: str) -> Optional[DataCollector]:
        return self.collectors.get(name)

    def should_profile(self, request: Request) -> bool:
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return False

        if self.sampling_rate < 1.0 and random.random() > self.sampling_rate:
            return False

        return True

    def collect(self, request: Request, response: Response) -> Optional[str]:
        if not self.enabled or not self.should_profile(request):
            return None

        current_day = self._get_today_folder()
        if self.storage_dir.name != current_day:
            self._setup_storage_directory()

        token = str(uuid.uuid4())

        profile_data = {
            "url": str(request.url),
            "method": request.method,
            "time": datetime.datetime.now().isoformat(),
            "token": token,
        }

        for name, collector in self.collectors.items():
            try:
                collector.collect(request, response)
                profile_data[name] = collector.get_data()
            except Exception as e:
                self.logger.error(f"Error collecting data from {name}: {str(e)}")

        self.profiles_cache[token] = profile_data
        self._maintain_cache_size()
        self._save_profile(token, profile_data)

        return token

    def get_profile(self, token: str) -> Dict:
        if token in self.profiles_cache:
            return self.profiles_cache[token]

        profile_path = self.storage_dir / f"{token}.json"
        if profile_path.exists():
            with open(profile_path, "r") as f:
                profile_data = json.load(f)
                self.profiles_cache[token] = profile_data
                self._maintain_cache_size()
                return profile_data

        if not token.endswith(".json"):
            token_file = f"{token}.json"
        else:
            token_file = token

        for date_dir in self.base_storage_dir.iterdir():
            if date_dir.is_dir():
                profile_path = date_dir / token_file
                if profile_path.exists():
                    with open(profile_path, "r") as f:
                        profile_data = json.load(f)
                        self.profiles_cache[token] = profile_data
                        self._maintain_cache_size()
                        return profile_data

        return {}

    def list_profiles(self, limit: int = 100, page: int = 1) -> List[Dict]:
        profiles = []
        offset = (page - 1) * limit
        count = 0

        date_dirs = sorted(
            [d for d in self.base_storage_dir.iterdir() if d.is_dir()],
            key=lambda d: d.name,
            reverse=True,
        )

        for date_dir in date_dirs:
            if count >= offset + limit:
                break

            files = sorted(
                [f for f in date_dir.glob("*.json") if f.is_file()],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )

            for file_path in files:
                if count < offset:
                    count += 1
                    continue

                if count >= offset + limit:
                    break

                try:
                    with open(file_path, "r") as f:
                        profile_data = json.load(f)
                        summary = {
                            "token": file_path.stem,
                            "url": profile_data.get("url", ""),
                            "method": profile_data.get("method", ""),
                            "time": profile_data.get("time", ""),
                            "status_code": profile_data.get("request", {}).get("status_code", 0),
                            "duration": profile_data.get("time", {}).get("duration", 0),
                        }
                        profiles.append(summary)
                        count += 1
                except Exception as e:
                    self.logger.error(f"Error reading profile {file_path}: {str(e)}")

        return profiles

    def _save_profile(self, token: str, data: Dict) -> None:
        try:
            files = list(self.storage_dir.glob("*.json"))

            if len(files) >= self.max_profiles_per_day:
                oldest_file = self._find_oldest_profile()
                if oldest_file and oldest_file.exists():
                    oldest_file.unlink()

            profile_path = self.storage_dir / f"{token}.json"
            with open(profile_path, "w") as f:
                json.dump(data, f, default=str)

        except Exception as e:
            self.logger.error(f"Error saving profile {token}: {str(e)}")
