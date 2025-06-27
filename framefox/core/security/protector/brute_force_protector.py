import logging
import time
from collections import defaultdict
from typing import Dict, Optional

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class BruteForceProtector:
    """
    Balanced brute force protection for extreme cases only.

    This class provides protection against brute force attacks by tracking
    login attempts per IP address and username. It implements progressive
    delays and blocking mechanisms for extreme cases only, maintaining
    a balance between security and usability.

    Features:
    - IP-based attempt tracking and blocking
    - Username-based attempt tracking and account locking
    - Progressive delay implementation
    - Automatic cleanup of old attempts
    - Risk level assessment
    """

    def __init__(self):
        self.logger = logging.getLogger("BRUTE_FORCE_PROTECTOR")
        self.login_attempts = defaultdict(list)
        self.user_attempts = defaultdict(list)
        self.blocked_ips = {}
        self.locked_accounts = {}

    def check_login_attempt(self, client_ip: str, username: str, success: bool = False) -> tuple[bool, Optional[str], int]:
        """
        Check if login attempt should be allowed.
        Only protects against extreme brute force cases.

        Returns:
            (is_allowed, reason_if_blocked, delay_seconds)
        """
        current_time = time.time()

        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                remaining = int(self.blocked_ips[client_ip] - current_time)
                return False, f"IP blocked for {remaining}s", 0
            else:
                del self.blocked_ips[client_ip]

        if username in self.locked_accounts:
            if current_time < self.locked_accounts[username]:
                remaining = int(self.locked_accounts[username] - current_time)
                return False, f"Account locked for {remaining}s", 0
            else:
                del self.locked_accounts[username]

        cutoff_time = current_time - 21600
        self.login_attempts[client_ip] = [t for t in self.login_attempts[client_ip] if t > cutoff_time]
        self.user_attempts[username] = [t for t in self.user_attempts[username] if t > cutoff_time]

        if success:
            self.login_attempts[client_ip] = []
            self.user_attempts[username] = []
            return True, None, 0

        self.login_attempts[client_ip].append(current_time)
        self.user_attempts[username].append(current_time)

        # ip_recent_15min = len([t for t in self.login_attempts[client_ip] if t > current_time - 900])
        ip_recent_1hour = len([t for t in self.login_attempts[client_ip] if t > current_time - 3600])
        user_recent_30min = len([t for t in self.user_attempts[username] if t > current_time - 1800])
        user_recent_1hour = len([t for t in self.user_attempts[username] if t > current_time - 3600])

        delay = 0
        total_ip_attempts = len(self.login_attempts[client_ip])

        if total_ip_attempts >= 8:
            delay = min(30, 2 ** (total_ip_attempts - 8))

        if ip_recent_1hour >= 25:
            self.blocked_ips[client_ip] = current_time + 1800
            self.logger.warning(f"IP blocked for extreme brute force: {client_ip} ({ip_recent_1hour} attempts in 1h)")
            return False, "Too many failed attempts", delay

        if user_recent_1hour >= 15:
            self.locked_accounts[username] = current_time + 900
            self.logger.warning(f"Account locked for brute force: {username} ({user_recent_1hour} attempts in 1h)")
            return False, "Account temporarily locked", delay

        if user_recent_30min >= 8:
            self.logger.info(f"Suspicious login activity for {username}: {user_recent_30min} attempts in 30min")

        return True, None, delay

    def get_attempt_stats(self, client_ip: str, username: str) -> Dict:
        """Get statistics for monitoring."""
        current_time = time.time()

        ip_attempts_1h = len([t for t in self.login_attempts[client_ip] if t > current_time - 3600])
        user_attempts_1h = len([t for t in self.user_attempts[username] if t > current_time - 3600])
        ip_attempts_15min = len([t for t in self.login_attempts[client_ip] if t > current_time - 900])
        user_attempts_15min = len([t for t in self.user_attempts[username] if t > current_time - 900])

        return {
            "ip_attempts_last_hour": ip_attempts_1h,
            "user_attempts_last_hour": user_attempts_1h,
            "ip_attempts_last_15min": ip_attempts_15min,
            "user_attempts_last_15min": user_attempts_15min,
            "ip_blocked": client_ip in self.blocked_ips,
            "account_locked": username in self.locked_accounts,
            "risk_level": self._calculate_risk_level(ip_attempts_1h, user_attempts_1h),
        }

    def _calculate_risk_level(self, ip_attempts: int, user_attempts: int) -> str:
        """Calculate risk level for monitoring."""
        if ip_attempts >= 20 or user_attempts >= 12:
            return "HIGH"
        elif ip_attempts >= 10 or user_attempts >= 6:
            return "MEDIUM"
        elif ip_attempts >= 5 or user_attempts >= 3:
            return "LOW"
        else:
            return "NORMAL"
