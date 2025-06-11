import asyncio
import hashlib
import logging
import time
from secrets import compare_digest
from typing import Any, Callable, Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TimingAttackProtector:
    """
    Utility class to protect against timing attacks by ensuring constant execution time.
    """

    def __init__(self, min_execution_time: float = 0.2):
        """
        Initialize the timing attack protector.

        Args:
            min_execution_time: Minimum execution time in seconds (default: 200ms)
        """
        self.min_execution_time = min_execution_time
        self.logger = logging.getLogger("TIMING_PROTECTOR")

    async def protect_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute an async function with timing attack protection.

        Args:
            func: The async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function execution
        """
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            await self._ensure_min_time(start_time)

    def protect_sync(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a sync function with timing attack protection.

        Args:
            func: The sync function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function execution
        """
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self._ensure_min_time_sync(start_time)

    async def _ensure_min_time(self, start_time: float) -> None:
        """Ensure minimum execution time for async operations."""
        elapsed = time.time() - start_time
        if elapsed < self.min_execution_time:
            sleep_time = self.min_execution_time - elapsed
            await asyncio.sleep(sleep_time)

    def _ensure_min_time_sync(self, start_time: float) -> None:
        """Ensure minimum execution time for sync operations."""
        elapsed = time.time() - start_time
        if elapsed < self.min_execution_time:
            sleep_time = self.min_execution_time - elapsed
            time.sleep(sleep_time)

    def safe_compare(self, a: str, b: str) -> bool:
        """
        Perform a timing-safe string comparison.

        Args:
            a: First string to compare
            b: Second string to compare

        Returns:
            True if strings are equal, False otherwise
        """
        if not a or not b:
            return False

        return compare_digest(a, b)

    def safe_hash_compare(self, plain: str, hashed: str, salt: Optional[str] = None) -> bool:
        """
        Perform a timing-safe hash comparison.

        Args:
            plain: Plain text to compare
            hashed: Hashed value to compare against
            salt: Optional salt for hashing

        Returns:
            True if hash matches, False otherwise
        """
        if not plain or not hashed:
            return False

        # Create hash of plain text
        if salt:
            plain_with_salt = f"{plain}{salt}"
        else:
            plain_with_salt = plain

        plain_hash = hashlib.sha256(plain_with_salt.encode()).hexdigest()

        return compare_digest(plain_hash, hashed)

    async def protected_authentication(self, auth_func: Callable, *args, **kwargs) -> Any:
        """
        Execute authentication with timing attack protection.

        Args:
            auth_func: The authentication function to execute
            *args: Arguments for the authentication function
            **kwargs: Keyword arguments for the authentication function

        Returns:
            The result of the authentication
        """
        return await self.protect_async(auth_func, *args, **kwargs)

    async def protected_csrf_validation(self, csrf_func: Callable, *args, **kwargs) -> bool:
        """
        Execute CSRF validation with timing attack protection.

        Args:
            csrf_func: The CSRF validation function
            *args: Arguments for the CSRF function
            **kwargs: Keyword arguments for the CSRF function

        Returns:
            True if CSRF is valid, False otherwise
        """
        return await self.protect_async(csrf_func, *args, **kwargs)

    def get_constant_time_decorator(self, min_time: Optional[float] = None):
        """
        Get a decorator for constant-time execution.

        Args:
            min_time: Override minimum time for this decorator

        Returns:
            A decorator function
        """
        execution_time = min_time or self.min_execution_time

        def decorator(func):
            if asyncio.iscoroutinefunction(func):

                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        elapsed = time.time() - start_time
                        if elapsed < execution_time:
                            await asyncio.sleep(execution_time - elapsed)

                return async_wrapper
            else:

                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        elapsed = time.time() - start_time
                        if elapsed < execution_time:
                            time.sleep(execution_time - elapsed)

                return sync_wrapper

        return decorator
