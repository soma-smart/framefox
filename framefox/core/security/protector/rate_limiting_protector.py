import logging
import time
from collections import defaultdict, deque
from typing import Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class RateLimitingProtector:
    """
    Balanced rate limiting focused on extreme abuse prevention.

    This class provides rate limiting functionality with configurable thresholds
    and burst protection. It's designed to be lenient for normal usage while
    blocking only extreme abuse patterns.

    Attributes:
        windows (defaultdict): Stores request timestamps per client/endpoint
        failed_attempts (defaultdict): Tracks failed attempts for progressive blocking
        blocked_ips (dict): Stores temporarily blocked IPs with expiration times
    """

    def __init__(self):
        self.logger = logging.getLogger("RATE_LIMITER")
        self.windows = defaultdict(deque)
        self.failed_attempts = defaultdict(int)
        self.blocked_ips = {}

    def is_allowed(
        self,
        client_ip: str,
        endpoint: str = "default",
        max_requests: int = 200,
        window_seconds: int = 60,
        burst_protection: bool = True,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed with lenient rate limiting.
        Only blocks extreme abuse cases.

        Returns:
            (is_allowed, reason_if_blocked)
        """
        current_time = time.time()
        key = f"{client_ip}:{endpoint}"

        if key in self.blocked_ips:
            if current_time < self.blocked_ips[key]:
                return False, "IP temporarily blocked"
            else:
                del self.blocked_ips[key]

        window = self.windows[key]
        cutoff_time = current_time - window_seconds

        while window and window[0] < cutoff_time:
            window.popleft()

        if burst_protection and len(window) > 0:
            recent_requests = sum(1 for t in window if t > current_time - 10)
            if recent_requests > 50:
                self._block_ip(key, 300)
                return False, "Extreme burst detected"

        if len(window) >= max_requests:
            self.failed_attempts[key] += 1
            if self.failed_attempts[key] > 5:
                block_duration = min(1800, 120 * self.failed_attempts[key])
                self._block_ip(key, block_duration)
                return False, f"Rate limit exceeded, blocked for {block_duration}s"
            return False, "Rate limit exceeded"

        window.append(current_time)
        if key in self.failed_attempts:
            self.failed_attempts[key] = max(0, self.failed_attempts[key] - 1)

        return True, None

    def _block_ip(self, key: str, duration: int):
        """Block IP for specified duration."""
        self.blocked_ips[key] = time.time() + duration
        self.logger.warning(f"IP blocked: {key} for {duration}s")

    def is_suspicious_pattern(self, client_ip: str, user_agent: str) -> bool:
        """Detect suspicious patterns but be more lenient."""
        very_suspicious_agents = [
            "masscan",
            "nmap",
            "sqlmap",
            "nikto",
            "dirb",
            "gobuster",
            "burpsuite",
            "zaproxy",
            "nuclei",
        ]

        return any(agent in user_agent.lower() for agent in very_suspicious_agents)
