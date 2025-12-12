import hashlib

from sanic import Sanic, Request
from json import dumps


def sanitize_for_json(data: dict) -> dict:
    """
    Sanitize dictionary data to ensure it can be safely serialized to JSON
    and stored in PostgreSQL. Replaces invalid Unicode surrogate pairs.
    
    :param data: Dictionary to sanitize
    :return: Sanitized dictionary
    """
    def sanitize_string(s: str) -> str:
        """Replace invalid surrogate pairs with replacement character"""
        try:
            # Encode with surrogatepass to handle unpaired surrogates,
            # then decode with replace to convert them to safe characters
            return s.encode('utf-8', errors='surrogatepass').decode('utf-8', errors='replace')
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If any encoding error occurs, use strict replacement
            return s.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    
    sanitized = {}
    for key, value in data.items():
        # Sanitize both keys and values
        safe_key = sanitize_string(key) if isinstance(key, str) else key
        
        if isinstance(value, str):
            sanitized[safe_key] = sanitize_string(value)
        elif isinstance(value, list):
            # Handle list values (common in query parameters)
            sanitized[safe_key] = [sanitize_string(v) if isinstance(v, str) else v for v in value]
        else:
            sanitized[safe_key] = value
    
    return sanitized


class Analytics:
    """
    Classe pour les statistiques d'analyse des requêtes
    """
    def __init__(self, app: Sanic) -> None:
        """
        Initialisation de la classe

        :param app: Sanic
        """

        @app.on_response(priority=999)
        async def after_request(request: Request, response):
            """
            Middleware pour suivre les réponses

            :param request: Request
            :param response: Response
            """

            headers = request.headers
            if "cookie" in headers:
                del headers["cookie"]

            await app.ctx.analytics.execute(
                """
                INSERT INTO requests_logs (
                    id, 
                    key, 
                    method, 
                    path, 
                    status, 
                    params, 
                    request_headers, 
                    ratelimit_limit, 
                    ratelimit_remaining, 
                    ratelimit_used, 
                    ratelimit_reset, 
                    ratelimit_bucket, 
                    process_time, 
                    api_version,
                    hashed_ip
                ) VALUES (
                    $1, 
                    $2, 
                    $3, 
                    $4, 
                    $5, 
                    $6, 
                    $7, 
                    $8, 
                    $9, 
                    $10, 
                    $11, 
                    $12, 
                    $13, 
                    $14,
                    $15
                );
                """,
                request.ctx.request_id,
                headers.get("x-api-key", None),
                request.method,
                request.path,
                response.status,
                dumps(sanitize_for_json(dict(request.args))),
                dumps(sanitize_for_json(dict(headers))),
                response.headers.get("x-ratelimit-limit", -1),
                response.headers.get("x-ratelimit-remaining", -1),
                response.headers.get("x-ratelimit-used", -1),
                response.headers.get("x-ratelimit-reset", -1),
                response.headers.get("x-ratelimit-bucket", -1),
                request.ctx.process_time,
                app.config.API_VERSION,
                hashlib.blake2b(request.headers.get('CF-Connecting-IP', request.client_ip).encode(), digest_size=20).hexdigest()
            )
