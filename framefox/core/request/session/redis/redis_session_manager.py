import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class RedisSessionManager:
    """
    Redis-based session manager for Framefox.

    This class handles session storage using Redis when configured.
    Falls back gracefully if Redis is not available.
    """

    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger("REDIS_SESSION_MANAGER")
        self.redis_client = None
        self.prefix = self.settings.session_redis_prefix
        self.enabled = False

        if self.settings.session_redis_enabled:
            self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection - logs error if fails"""
        try:
            from urllib.parse import urlparse

            import redis

            # Parse Redis URL
            url = self.settings.session_redis_url
            parsed = urlparse(url)

            # Create Redis client
            self.redis_client = redis.Redis(
                host=parsed.hostname or "localhost",
                port=parsed.port or 6379,
                db=self.settings.session_redis_db,
                password=parsed.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            self.redis_client.ping()
            self.enabled = True

        except ImportError as e:
            self.logger.error(f"Redis package not installed: {e}. To enable Redis sessions, install with: pip install redis")
            self.enabled = False
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis session storage: {e}")
            self.enabled = False

    def is_enabled(self) -> bool:
        """Check if Redis is available"""
        return self.enabled and self.redis_client is not None

    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"{self.prefix}{session_id}"

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve a session by its ID"""
        if not self.is_enabled():
            return None

        try:
            key = self._get_key(session_id)
            session_data = self.redis_client.hgetall(key)

            if not session_data:
                return None

            # Check if session has expired
            expires_at = float(session_data.get("expires_at", 0))
            current_time = datetime.now(timezone.utc).timestamp()

            if expires_at < current_time:
                self.delete_session(session_id)
                return None

            return {
                "data": json.loads(session_data.get("data", "{}")),
                "expires_at": expires_at,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving session {session_id} from Redis: {e}")
            return None

    def create_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Create a new session"""
        if not self.is_enabled():
            return

        try:
            key = self._get_key(session_id)
            expires_at = datetime.now(timezone.utc).timestamp() + max_age

            session_data = {"data": json.dumps(data), "expires_at": str(expires_at)}

            # Store in Redis with TTL
            self.redis_client.hset(key, mapping=session_data)
            self.redis_client.expire(key, max_age)

        except Exception as e:
            self.logger.error(f"Error creating session {session_id} in Redis: {e}")

    def update_session(self, session_id: str, data: Dict, max_age: int) -> None:
        """Update an existing session and reset its expiration time"""
        if not self.is_enabled():
            return

        try:
            key = self._get_key(session_id)
            expires_at = datetime.now(timezone.utc).timestamp() + max_age

            session_data = {"data": json.dumps(data), "expires_at": str(expires_at)}

            self.redis_client.hset(key, mapping=session_data)
            self.redis_client.expire(key, max_age)

        except Exception as e:
            self.logger.error(f"Error updating session {session_id} in Redis: {e}")

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if not self.is_enabled():
            return False

        try:
            key = self._get_key(session_id)
            result = self.redis_client.delete(key)
            return result > 0

        except Exception as e:
            self.logger.error(f"Error deleting session {session_id} from Redis: {e}")
            return False

    def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions (Redis handles TTL automatically)"""
        if not self.is_enabled():
            return

        try:

            pattern = f"{self.prefix}*"
            current_time = datetime.now(timezone.utc).timestamp()

            for key in self.redis_client.scan_iter(match=pattern, count=100):
                try:
                    session_data = self.redis_client.hgetall(key)
                    if session_data:
                        expires_at = float(session_data.get("expires_at", 0))
                        if expires_at < current_time:
                            self.redis_client.delete(key)
                except Exception:
                    continue

        except Exception as e:
            self.logger.error(f"Error during Redis session cleanup: {e}")

    def load_sessions(self) -> Dict:
        """Load all sessions (compatibility method - not efficient for Redis)"""
        return {}

    def save_sessions(self, session_store: Dict) -> None:
        """Save sessions (compatibility method - not used with Redis)"""
        pass
