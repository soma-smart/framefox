import html
import logging
import re
from typing import Any, Dict, List

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class InputValidationProtector:
    """
    Smart input validation protector that minimizes false positives while maintaining security.

    This class provides comprehensive input validation and sanitization capabilities
    for web applications, protecting against XSS, SQL injection, and path traversal attacks.
    It uses context-aware validation to reduce false positives and improve user experience.

    Attributes:
        strict_mode (bool): Enable strict validation mode for enhanced security
        xss_patterns (List[str]): Regular expressions for XSS attack detection
        sql_patterns (List[str]): Regular expressions for SQL injection detection
        path_traversal_patterns (List[str]): Regular expressions for path traversal detection

    Example:
        >>> protector = InputValidationProtector(strict_mode=False)
        >>> clean_data, threats = protector.validate_and_sanitize(user_input, "username", "form")
        >>> if threats:
        ...     print(f"Security threats detected: {threats}")
    """

    def __init__(self, strict_mode: bool = False):
        self.logger = logging.getLogger("INPUT_VALIDATOR")
        self.strict_mode = strict_mode

        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:\s*[^\/]",
            r"vbscript:",
            r'on\w+\s*=\s*["\'][^"\']*["\']',
            r"expression\s*\(",
            r"<iframe[^>]*src\s*=",
            r"<object[^>]*data\s*=",
            r"<embed[^>]*src\s*=",
        ]

        self.sql_patterns = [
            r"(\bUNION\s+ALL\s+SELECT\b)",
            r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b.*[\'\"]\s*=\s*[\'\"]\s*OR\b)",
            r"(\bDROP\s+TABLE\b)",
            r"(\bDELETE\s+FROM\b.*\bWHERE\b.*[\'\"]\s*=\s*[\'\"]\s*OR\b)",
            r"(\bINSERT\s+INTO\b.*\bVALUES\b.*\bSELECT\b)",
            r"(\bEXEC\s*\(\s*[\'\"]\s*[^\'\"]*[\'\"]\s*\))",
            r"(\bSHUTDOWN\s*(\(|\b))",
            r"([\'\"]\s*;\s*(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER)\b)",
        ]

        self.path_traversal_patterns = [
            r"\.\.\/.*\.\.",
            r"\.\.\\.*\.\.",
            r"\/etc\/passwd",
            r"\/proc\/version",
            r"file:\/\/.*\/etc\/",
            r"php:\/\/filter",
        ]

    def validate_and_sanitize(self, data: Any, field_name: str = "unknown", context: str = "form") -> tuple[Any, List[str]]:
        """
        Smart validation that considers context.

        Args:
            data: Data to validate
            field_name: Name of the field
            context: Context like 'form', 'json', 'comment', 'html_content'
        """
        threats = []

        if isinstance(data, str):
            return self._validate_string(data, field_name, threats, context)
        elif isinstance(data, dict):
            return self._validate_dict(data, field_name, threats, context)
        elif isinstance(data, list):
            return self._validate_list(data, field_name, threats, context)
        else:
            return data, threats

    def _validate_string(self, value: str, field_name: str, threats: List[str], context: str) -> tuple[str, List[str]]:
        """Smart string validation based on context."""
        original_value = value

        if len(value) > 50000:
            threats.append(f"OVERSIZED_INPUT:{field_name}")
            value = value[:50000]

        if context not in ["html_content", "rich_text"]:
            for pattern in self.xss_patterns:
                if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                    threats.append(f"XSS_ATTEMPT:{field_name}")
                    self.logger.warning(f"XSS attempt detected in {field_name}")
                    break

        if context in ["form", "search", "filter"]:
            for pattern in self.sql_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    threats.append(f"SQL_INJECTION:{field_name}")
                    self.logger.warning(f"SQL injection attempt in {field_name}")
                    break

        if context in ["file", "path", "upload"] or "file" in field_name.lower():
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    threats.append(f"PATH_TRAVERSAL:{field_name}")
                    self.logger.warning(f"Path traversal attempt in {field_name}")
                    break

        if context == "form" and len(threats) > 0:
            value = html.escape(value)
        elif context == "search":
            value = re.sub(r'[<>"\']', "", value)

        value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)

        return value, threats

    def _validate_dict(self, data: Dict, field_name: str, threats: List[str], context: str) -> tuple[Dict, List[str]]:
        """Smart dictionary validation."""
        sanitized = {}
        for key, value in data.items():
            clean_key = str(key)
            if len(clean_key) > 100:
                clean_key = clean_key[:100]
                threats.append(f"OVERSIZED_KEY:{field_name}")

            sanitized_value, sub_threats = self.validate_and_sanitize(value, f"{field_name}.{key}", context)
            sanitized[clean_key] = sanitized_value
            threats.extend(sub_threats)
        return sanitized, threats

    def _validate_list(self, data: List, field_name: str, threats: List[str], context: str) -> tuple[List, List[str]]:
        """Smart list validation."""
        if len(data) > 1000:
            threats.append(f"OVERSIZED_ARRAY:{field_name}")
            data = data[:1000]

        sanitized = []
        for i, item in enumerate(data):
            sanitized_item, sub_threats = self.validate_and_sanitize(item, f"{field_name}[{i}]", context)
            sanitized.append(sanitized_item)
            threats.extend(sub_threats)
        return sanitized, threats

    def is_malicious_payload(self, payload: str) -> bool:
        """Quick check for obviously malicious payloads."""
        dangerous_indicators = [
            "eval(",
            "exec(",
            "system(",
            "shell_exec(",
            "passthru(",
            "<?php",
            "<%",
            "<script>alert",
            "javascript:alert",
            "data:text/html,<script",
            "/etc/passwd",
            "file://",
        ]

        payload_lower = payload.lower()
        return any(indicator in payload_lower for indicator in dangerous_indicators)
