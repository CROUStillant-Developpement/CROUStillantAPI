import hashlib

from sanic import Sanic, Request
from json import dumps


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
                dumps(dict(request.args)),
                dumps(dict(headers)),
                response.headers.get("x-ratelimit-limit", -1),
                response.headers.get("x-ratelimit-remaining", -1),
                response.headers.get("x-ratelimit-used", -1),
                response.headers.get("x-ratelimit-reset", -1),
                response.headers.get("x-ratelimit-bucket", -1),
                request.ctx.process_time,
                app.config.API_VERSION,
                hashlib.blake2b(request.ip.encode(), digest_size=20).hexdigest()
            )
