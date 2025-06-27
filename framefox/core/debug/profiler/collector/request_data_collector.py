import json
import re
import urllib.parse
from typing import Any, Dict

from fastapi import Request, Response

from framefox.core.debug.profiler.collector.data_collector import DataCollector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class RequestDataCollector(DataCollector):
    """
    Collects and filters HTTP request data for profiling and debugging purposes.
    Sensitive fields are masked to avoid leaking confidential information.
    Designed for use with FastAPI requests and responses.
    """

    def __init__(self):
        super().__init__("request", "fa-globe")
        self.request_body = None
        self.form_data = None
        self.sensitive_fields = {
            "password",
            "passwd",
            "pwd",
            "secret",
            "token",
            "key",
            "api_key",
            "auth_token",
            "access_token",
            "refresh_token",
            "csrf_token",
            "credit_card",
            "card_number",
            "cvv",
            "ssn",
            "social_security",
            "private_key",
            "client_secret",
            "auth_secret",
            "session_id",
            "cookie",
            "authorization",
        }

    def _is_sensitive_field(self, field_name: str) -> bool:
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.sensitive_fields)

    def _filter_sensitive_data(self, data: Any) -> Any:
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if self._is_sensitive_field(key):
                    filtered[key] = "***FILTERED***"
                else:
                    filtered[key] = self._filter_sensitive_data(value)
            return filtered
        elif isinstance(data, list):
            return [self._filter_sensitive_data(item) for item in data]
        else:
            return data

    def _parse_form_data(self, raw_body: str) -> Dict[str, Any]:
        try:
            parsed = urllib.parse.parse_qs(raw_body, keep_blank_values=True)
            result = {}
            for key, values in parsed.items():
                if len(values) == 1:
                    result[key] = values[0]
                else:
                    result[key] = values
            return result
        except Exception:
            return {"_raw_body": raw_body}

    def _clean_raw_body(self, raw_body: str, content_type: str) -> Dict[str, Any]:
        if not raw_body:
            return {"_no_data": "Empty request body"}
        if "application/x-www-form-urlencoded" in content_type:
            parsed_data = self._parse_form_data(raw_body)
            filtered_data = self._filter_sensitive_data(parsed_data)
            return {
                "_form_data": filtered_data,
                "_raw_body_filtered": self._mask_sensitive_in_raw_body(raw_body),
            }
        elif "application/json" in content_type:
            try:
                json_data = json.loads(raw_body)
                filtered_data = self._filter_sensitive_data(json_data)
                return {"_json_data": filtered_data, "_original_type": "json"}
            except json.JSONDecodeError:
                return {"_raw_body": self._mask_sensitive_in_raw_body(raw_body)}
        else:
            return {"_raw_body": self._mask_sensitive_in_raw_body(raw_body)}

    def _mask_sensitive_in_raw_body(self, raw_body: str) -> str:
        patterns = []
        for field in self.sensitive_fields:
            patterns.append(rf"({field}[^=]*=)[^&]*(&|$)")
            patterns.append(rf'("{field}"[^:]*:\s*")[^"]*(")')
            patterns.append(rf'("{field}"[^:]*:\s*)[^,}}\]]*')
        masked_body = raw_body
        for pattern in patterns:
            if re.search(pattern, masked_body, re.IGNORECASE):
                masked_body = re.sub(
                    pattern,
                    lambda m: f"{m.group(1)}***FILTERED***{m.group(2) if len(m.groups()) > 1 and m.group(2) else ''}",
                    masked_body,
                    flags=re.IGNORECASE,
                )
        return masked_body

    async def capture_request_body(self, request: Request):
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if not body:
                    self.request_body = {"_no_data": "Empty request body"}
                    return
                content_type = request.headers.get("content-type", "")
                try:
                    body_str = body.decode("utf-8", errors="ignore")
                    self.request_body = self._clean_raw_body(body_str, content_type)
                except UnicodeDecodeError:
                    self.request_body = {"_error": "Could not decode request body (binary data?)"}
            except Exception as e:
                self.request_body = {"_error": f"Could not capture request body: {str(e)}"}

    def collect(self, request: Request, response: Response) -> None:
        headers = dict(request.headers)
        sensitive_headers = {
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
            "x-csrf-token",
        }
        filtered_headers = {k: v if k.lower() not in sensitive_headers else "***FILTERED***" for k, v in headers.items()}
        query_params = dict(request.query_params)
        filtered_query_params = self._filter_sensitive_data(query_params)
        request_data = None
        if hasattr(request, "state") and hasattr(request.state, "form_data"):
            request_data = self._filter_sensitive_data(request.state.form_data)
        elif self.request_body:
            request_data = self.request_body
        if request_data is None and request.method in ("POST", "PUT", "PATCH"):
            request_data = {"_no_data": "No request body captured"}
        client_info = {
            "host": request.client.host if request.client else "unknown",
            "port": request.client.port if request.client else "unknown",
        }
        response_headers = dict(response.headers) if hasattr(response, "headers") else {}
        self.data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": filtered_query_params,
            "headers": filtered_headers,
            "client": client_info,
            "status_code": (response.status_code if hasattr(response, "status_code") else 200),
            "response_headers": response_headers,
            "request_data": request_data,
            "content_type": request.headers.get("content-type", ""),
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", ""),
        }

    def reset(self):
        self.data = {}
        self.request_body = None
        self.form_data = None
