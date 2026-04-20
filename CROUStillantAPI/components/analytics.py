import asyncio
import hashlib

from sanic import Sanic, Request
from json import dumps


def sanitize_for_json(data: dict) -> dict:
    """
    Assainit un dictionnaire pour qu'il puisse être sérialisé en JSON
    et stocké dans PostgreSQL. Remplace les paires de substitution Unicode invalides.

    :param data: Dictionnaire à assainir
    :return: Dictionnaire assaini
    """

    def sanitize_string(s: str) -> str:
        """
        Remplace les paires de substitution invalides par le caractère de remplacement

        :param s: Chaîne à assainir
        :return: Chaîne assainie
        """
        return s.encode("utf-8", errors="surrogatepass").decode(
            "utf-8", errors="replace"
        )

    sanitized = {}
    for key, value in data.items():
        safe_key = sanitize_string(key) if isinstance(key, str) else key

        if isinstance(value, str):
            sanitized[safe_key] = sanitize_string(value)
        elif isinstance(value, list):
            sanitized[safe_key] = [
                sanitize_string(v) if isinstance(v, str) else v for v in value
            ]
        else:
            sanitized[safe_key] = value

    return sanitized


_INSERT_SQL = """
    INSERT INTO requests_logs (
        id, key, method, path, status, params, request_headers,
        ratelimit_limit, ratelimit_remaining, ratelimit_used,
        ratelimit_reset, ratelimit_bucket, process_time,
        api_version, hashed_ip
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
    )
"""

_BATCH_SIZE = 500
_FLUSH_INTERVAL = 10  # seconds


class Analytics:
    """
    Classe pour les statistiques d'analyse des requêtes.

    Les entrées de log sont accumulées dans une file en mémoire et insérées
    en base de données par lots via un flush périodique, afin de réduire
    la pression en écriture sur PostgreSQL.
    """

    def __init__(self, app: Sanic) -> None:
        """
        Initialise la classe et enregistre les middlewares et listeners Sanic

        :param app: Instance de l'application Sanic
        """
        self._queue: list = []
        self._pool = None

        @app.on_response(priority=999)
        async def after_request(request: Request, response):
            """
            Middleware exécuté après chaque réponse.
            Enqueue les métadonnées de la requête pour insertion différée.

            :param request: Request
            :param response: Response
            """
            headers = dict(request.headers)
            if "cookie" in headers:
                del headers["cookie"]

            self._queue.append((
                request.ctx.request_id,
                headers.get("x-api-key", None),
                request.method,
                request.path,
                response.status,
                dumps(sanitize_for_json(dict(request.args))),
                dumps(sanitize_for_json(headers)),
                response.headers.get("x-ratelimit-limit", -1),
                response.headers.get("x-ratelimit-remaining", -1),
                response.headers.get("x-ratelimit-used", -1),
                response.headers.get("x-ratelimit-reset", -1),
                response.headers.get("x-ratelimit-bucket", -1),
                request.ctx.process_time,
                app.config.API_VERSION,
                hashlib.blake2b(
                    request.headers.get("CF-Connecting-IP", request.client_ip).encode(),
                    digest_size=20,
                ).hexdigest(),
            ))

            if len(self._queue) >= _BATCH_SIZE:
                await self._flush()

        @app.after_server_start
        async def start_flush_task(app, loop):
            """
            Démarre la tâche de flush périodique après le démarrage du serveur

            :param app: Instance de l'application Sanic
            :param loop: Boucle d'événements asyncio
            """
            self._pool = app.ctx.pool
            app.add_task(self._flush_loop(), name="analytics_flush")

        @app.before_server_stop
        async def drain_queue(app, loop):
            """
            Vide la file d'attente avant l'arrêt du serveur pour éviter toute perte de données

            :param app: Instance de l'application Sanic
            :param loop: Boucle d'événements asyncio
            """
            await self._flush()

    async def _flush(self) -> None:
        """
        Insère en base de données tous les logs accumulés dans la file d'attente.
        En cas d'erreur transitoire, les entrées sont remises en file pour le prochain flush.
        """
        if not self._queue or not self._pool:
            return
        batch, self._queue = self._queue, []
        try:
            async with self._pool.acquire() as conn:
                await conn.executemany(_INSERT_SQL, batch)
        except Exception:
            self._queue = batch + self._queue

    async def _flush_loop(self) -> None:
        """
        Tâche de fond qui déclenche un flush à intervalle régulier défini par ``_FLUSH_INTERVAL``.
        S'arrête proprement à l'annulation de la tâche (arrêt du serveur).
        """
        while True:
            try:
                await asyncio.sleep(_FLUSH_INTERVAL)
                await self._flush()
            except asyncio.CancelledError:
                break
