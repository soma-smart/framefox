import hashlib
import hmac
import inspect
import logging
from functools import wraps
from typing import List, Optional

from fastapi import HTTPException, Request
from starlette.responses import JSONResponse

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class WebHook:
    """
    Decorator class for managing WebHook routes with automatic signature verification and payload handling.

    Args:
        path (str): The WebHook route path.
        name (str): The name of the WebHook route.
        secret (Optional[str], optional): Secret key for signature verification. Defaults to None.
        signature_header (str, optional): Header containing the webhook signature. Defaults to "X-Hub-Signature-256".
        verify_signature (bool, optional): Whether to verify webhook signatures. Defaults to True.
        allowed_ips (Optional[List[str]], optional): List of allowed IP addresses. Defaults to None.
        timeout (int, optional): Request timeout in seconds. Defaults to 30.
        auto_respond (bool, optional): Whether to automatically send 200 OK response. Defaults to True.
    """

    def __init__(
        self,
        path: str,
        name: str,
        secret: Optional[str] = None,
        signature_header: str = "X-Hub-Signature-256",
        verify_signature: bool = True,
        allowed_ips: Optional[List[str]] = None,
        timeout: int = 30,
        auto_respond: bool = True,
    ):
        self.path = path
        self.name = name
        self.secret = secret
        self.signature_header = signature_header
        self.verify_signature = verify_signature
        self.allowed_ips = allowed_ips or []
        self.timeout = timeout
        self.auto_respond = auto_respond
        self.logger = logging.getLogger("WEBHOOK")

    def __call__(self, func):
        self._original_func = func
        original_sig = inspect.signature(func)

        decorator_self = self

        @wraps(func)
        async def wrapper(controller_self, request: Request, **path_params):
            try:
                # Vérification IP si configurée
                if decorator_self.allowed_ips:
                    client_ip = decorator_self._get_client_ip(request)
                    if client_ip not in decorator_self.allowed_ips:
                        decorator_self.logger.warning(f"Webhook access denied for IP: {client_ip}")
                        raise HTTPException(status_code=403, detail="IP not allowed")

                # Lecture du payload
                body = await request.body()

                # Vérification de la signature si activée
                if decorator_self.verify_signature and decorator_self.secret:
                    signature = request.headers.get(decorator_self.signature_header)
                    if not decorator_self._verify_signature(body, signature):
                        decorator_self.logger.warning("Webhook signature verification failed")
                        raise HTTPException(status_code=401, detail="Invalid signature")

                # Extraction des paramètres d'URL
                extracted_params = {}
                if path_params:
                    extracted_params.update(path_params)

                # Parsing du payload JSON
                try:
                    import json

                    payload = json.loads(body.decode("utf-8")) if body else {}
                except json.JSONDecodeError:
                    payload = {}

                # Exécution de la fonction webhook
                result = await func(controller_self, request, payload, **extracted_params)

                # Réponse automatique si activée
                if decorator_self.auto_respond:
                    if result is None:
                        return JSONResponse(content={"status": "ok"}, status_code=200)
                    elif isinstance(result, dict):
                        return JSONResponse(content=result, status_code=200)
                    else:
                        return result
                else:
                    return result

            except HTTPException:
                raise
            except Exception as e:
                decorator_self.logger.error(f"Webhook error in {func.__name__}: {e}")
                if decorator_self.auto_respond:
                    return JSONResponse(content={"error": "Internal server error"}, status_code=500)
                raise

        # Création de la signature FastAPI
        wrapper.__signature__ = self._create_fastapi_signature(original_sig)
        wrapper.__annotations__ = func.__annotations__

        # Métadonnées du webhook
        wrapper.webhook_info = {
            "path": self.path,
            "name": self.name,
            "secret": self.secret,
            "signature_header": self.signature_header,
            "verify_signature": self.verify_signature,
            "allowed_ips": self.allowed_ips,
            "timeout": self.timeout,
            "auto_respond": self.auto_respond,
            "methods": ["POST"],  # Les webhooks sont généralement POST
        }

        return wrapper

    def _create_fastapi_signature(self, original_sig):
        """Crée la signature FastAPI pour le webhook"""
        new_params = []

        # Ajout du paramètre self
        for param_name, param in original_sig.parameters.items():
            if param_name == "self":
                new_params.append(param)
                break

        # Ajout du paramètre Request
        request_param = inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)
        new_params.append(request_param)

        # Ajout des paramètres de path si présents dans l'URL
        path_params = self._extract_path_parameters()
        for param_name in path_params:
            path_param = inspect.Parameter(param_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
            new_params.append(path_param)

        return inspect.Signature(new_params)

    def _extract_path_parameters(self) -> List[str]:
        """Extrait les paramètres de path de l'URL"""
        import re

        pattern = r"\{([^}]+)\}"
        return re.findall(pattern, self.path)

    def _get_client_ip(self, request: Request) -> str:
        """Récupère l'IP du client en tenant compte des proxies"""
        # Vérification des headers de proxy courants
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # IP directe
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _verify_signature(self, payload: bytes, signature: Optional[str]) -> bool:
        """Vérifie la signature du webhook"""
        if not signature or not self.secret:
            return False

        try:
            # Support pour différents formats de signature
            if signature.startswith("sha256="):
                expected_signature = "sha256=" + hmac.new(self.secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            elif signature.startswith("sha1="):
                expected_signature = "sha1=" + hmac.new(self.secret.encode("utf-8"), payload, hashlib.sha1).hexdigest()
            else:
                # Signature sans préfixe (format personnalisé)
                expected_signature = hmac.new(self.secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            self.logger.error(f"Signature verification error: {e}")
            return False
