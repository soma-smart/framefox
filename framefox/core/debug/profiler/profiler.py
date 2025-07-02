import datetime
import json
import logging
import random
import shutil
import traceback
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Request, Response

from framefox.core.config.settings import Settings
from framefox.core.debug.profiler.collector.data_collector import DataCollector
from framefox.core.debug.profiler.collector.exception_data_collector import (
    ExceptionDataCollector,
)
from framefox.core.debug.profiler.collector.log_data_collector import LogDataCollector
from framefox.core.debug.profiler.collector.memory_data_collector import (
    MemoryDataCollector,
)
from framefox.core.debug.profiler.collector.request_data_collector import (
    RequestDataCollector,
)
from framefox.core.debug.profiler.collector.route_data_collector import (
    RouteDataCollector,
)
from framefox.core.debug.profiler.collector.sentry_data_collector import (
    SentryDataCollector,
)
from framefox.core.debug.profiler.collector.sql_data_collector import SQLDataCollector
from framefox.core.debug.profiler.collector.time_data_collector import TimeDataCollector
from framefox.core.debug.profiler.collector.user_data_collector import UserDataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Profiler:
    """
    Singleton class for profiling HTTP requests in the Framefox framework.

    The Profiler manages data collectors, handles storage and retention of profiling data,
    and provides methods to enable/disable profiling, collect and retrieve profiles, and
    manage profile storage limits and retention policies.

    Attributes:
        settings: Application settings loaded from configuration.
        collectors: Registered data collectors for profiling.
        profiles_cache: In-memory cache of recent profiles.
        enabled: Whether profiling is currently enabled.
        max_profiles_in_memory: Maximum number of profiles to keep in memory.
        max_profiles_per_day: Maximum number of profiles to store per day.
        retention_days: Number of days to retain profile data.
        sampling_rate: Fraction of requests to profile (0.0 - 1.0).
        exclude_paths: List of URL paths to exclude from profiling.
        base_storage_dir: Base directory for storing profile data.
        logger: Logger for profiler events.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Profiler, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.settings = Settings()
        self.collectors = {}
        self.profiles_cache = {}
        self.enabled = False

        self.max_profiles_in_memory = self.settings.profiler_max_memory
        self.max_profiles_per_day = self.settings.profiler_max_files_per_day
        self.retention_days = self.settings.profiler_retention_days
        self.sampling_rate = self.settings.profiler_sampling_rate

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
        self.register_collector(UserDataCollector())
        self.register_collector(SentryDataCollector())

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
            self.logger.warning(
                f"Maximum number of profiles reached for today ({profile_count}/{self.max_profiles_per_day}). Replacing oldest profiles."
            )

    def _cleanup_old_profiles(self) -> None:
        try:
            if not self.base_storage_dir.exists():
                return

            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")

            for date_dir in self.base_storage_dir.iterdir():
                if date_dir.is_dir() and date_dir.name < cutoff_str:
                    shutil.rmtree(date_dir)
        except Exception as e:
            self.logger.error(f"Error cleaning up old profiles: {str(e)}")

    def _maintain_cache_size(self) -> None:
        if len(self.profiles_cache) > self.max_profiles_in_memory:
            sorted_keys = sorted(self.profiles_cache.keys())
            keys_to_remove = sorted_keys[: -self.max_profiles_in_memory]
            for key in keys_to_remove:
                self.profiles_cache.pop(key, None)
            self.logger.debug(f"Cleaned cache, removed {len(keys_to_remove)} profiles (max: {self.max_profiles_in_memory})")

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
            self.logger.debug(f"Request skipped due to sampling rate ({self.sampling_rate})")
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

        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, "reset"):
                    collector.reset()
            except Exception as e:
                self.logger.error(f"Error resetting collector {name}: {str(e)}")

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

                        time_data = profile_data.get("time", {})
                        request_data = profile_data.get("request", {})

                        summary = {
                            "token": file_path.stem,
                            "url": profile_data.get("url", ""),
                            "method": profile_data.get("method", ""),
                            "time": profile_data.get("time", ""),
                            "status_code": request_data.get("status_code", 0),
                            "duration": (time_data.get("duration", 0) if isinstance(time_data, dict) else 0),
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
                    self.logger.debug(f"Removing oldest profile {oldest_file.name} (limit: {self.max_profiles_per_day})")
                    oldest_file.unlink()

            profile_path = self.storage_dir / f"{token}.json"
            with open(profile_path, "w") as f:
                json.dump(data, f, default=str)

        except Exception as e:
            self.logger.error(f"Error saving profile {token}: {str(e)}")

    def collect_error_profile(self, request: Request, exception: Exception) -> Optional[str]:
        """Create an error profile and return the token."""
        if not self.enabled:
            return None

        current_day = self._get_today_folder()
        if self.storage_dir.name != current_day:
            self._setup_storage_directory()

        token = str(uuid.uuid4())[:8]

        profile_data = {
            "url": str(request.url),
            "method": request.method,
            "time": datetime.datetime.now().isoformat(),
            "token": token,
            "is_error_profile": True,
        }

        for name, collector in self.collectors.items():
            try:
                if name == "exception":
                    collector.collect_exception(exception, traceback.format_exc())

                    from fastapi.responses import Response

                    fake_response = Response(status_code=500)
                    collector.collect(request, fake_response)

                elif name == "request":
                    from fastapi.responses import Response

                    fake_response = Response(status_code=500)
                    collector.collect(request, fake_response)

                elif name == "time":
                    start_time = getattr(
                        request.state,
                        "request_start_time",
                        datetime.datetime.now().timestamp(),
                    )
                    duration = datetime.datetime.now().timestamp() - start_time
                    collector.duration = duration * 1000
                    collector.collect(request, None)

                elif name in ["memory", "route", "user", "log"]:
                    try:
                        from fastapi.responses import Response

                        fake_response = Response(status_code=500)
                        collector.collect(request, fake_response)
                    except Exception:
                        pass

                collector_data = collector.get_data()
                profile_data[name] = collector_data

            except Exception as e:
                self.logger.error(f"Error collecting data from {name} for error profile: {str(e)}")

        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, "reset"):
                    collector.reset()
            except Exception as e:
                self.logger.error(f"Error resetting collector {name}: {str(e)}")

        self.profiles_cache[token] = profile_data
        self._maintain_cache_size()
        self._save_profile(token, profile_data)

        return token
