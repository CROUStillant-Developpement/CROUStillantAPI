import redis.asyncio as redis
import hashlib
import functools
import struct

from sanic import Sanic, Request
from sanic.response import HTTPResponse, JSONResponse
from redis import Redis
from dotenv import load_dotenv
from os import environ


def _serialize_response(response: HTTPResponse) -> bytes:
    """
    Sérialise une réponse HTTP en bytes compacts.

    Format binaire : ``[status: 2o][longueur content_type: 2o][content_type][body]``

    :param response: La réponse HTTP à sérialiser.
    :type response: HTTPResponse
    :return: La réponse sérialisée en bytes.
    :rtype: bytes
    """
    ct = (response.content_type or "").encode()
    header = struct.pack("!HH", response.status, len(ct))
    return header + ct + (response.body or b"")


def _deserialize_response(data: bytes) -> HTTPResponse:
    """
    Reconstruit une réponse HTTP à partir de bytes sérialisés.

    Format binaire attendu : ``[status: 2o][longueur content_type: 2o][content_type][body]``

    :param data: Les bytes à désérialiser.
    :type data: bytes
    :return: La réponse HTTP reconstruite.
    :rtype: HTTPResponse
    """
    status, ct_len = struct.unpack("!HH", data[:4])
    content_type = data[4:4 + ct_len].decode()
    body = data[4 + ct_len:]
    return HTTPResponse(body=body, status=status, content_type=content_type)


load_dotenv(dotenv_path=".env")


class Cache:
    """
    Classe pour gérer un cache avec Redis (Utilisation de redis-py au lieu de aioredis)
    """

    redis: Redis

    def __init__(
        self,
        app: Sanic,
        redis_url: str = f"redis://{environ.get('REDIS_HOST', 'localhost')}:{environ.get('REDIS_PORT', 6379)}",
    ):
        """
        Initialise la classe avec une connexion Redis

        :param app: Instance de l'application Sanic
        :param redis_url: URL de connexion à Redis
        """
        self.redis = None
        self.cache_ignored_statuses = {
            400,
            401,
            403,
            405,
            406,
            408,
            409,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            417,
            418,
            422,
            423,
            424,
            425,
            426,
            428,
            429,
            431,
            451,
            500,
            501,
            502,
            503,
            504,
            505,
            506,
            507,
            508,
            510,
            511,
        }

        @app.before_server_start
        async def setup_redis(app):
            """
            Connexion à Redis avant le démarrage du serveur
            """
            self.redis = redis.from_url(redis_url, decode_responses=False)

        @app.after_server_stop
        async def close_redis(app):
            """
            Ferme la connexion Redis après l'arrêt du serveur
            """
            if self.redis:
                await self.redis.close()

    async def get_cache_key(self, request: Request) -> str:
        """
        Génère une clé de cache basée sur l'URL et les paramètres de requête

        :param request: Request
        :return: Clé de cache unique
        """
        raw_key = request.url + str(sorted(request.args.items()))
        return hashlib.blake2b(raw_key.encode(), digest_size=16).hexdigest()

    async def get(
        self, request: Request, key: str = None
    ) -> JSONResponse | HTTPResponse | None:
        """
        Récupère la réponse mise en cache si elle existe

        :param request: Request
        :param key: Clé de cache (facultatif)
        :return: JSONResponse ou None
        """
        if not self.redis:
            return None

        if key:
            cache_key = key
        else:
            cache_key = await self.get_cache_key(request)

        cached_data = await self.redis.get(cache_key)

        if cached_data:
            return _deserialize_response(cached_data)

        return None

    async def set(
        self,
        request: Request,
        response: JSONResponse | HTTPResponse,
        ttl: int,
        key: str = None,
    ):
        """
        Stocke une réponse dans le cache si elle a un statut 200

        :param request: Request
        :param response: JSONResponse
        :param key: Clé de cache (facultatif)
        :param ttl: Durée de vie du cache en secondes
        """
        if not self.redis or response.status in self.cache_ignored_statuses:
            return
        else:
            if key:
                cache_key = key
            else:
                cache_key = await self.get_cache_key(request)

            cached_data = _serialize_response(response)
            await self.redis.setex(cache_key, ttl, cached_data)


def cache(ttl: int = 60, key: str = None):
    """
    Décorateur pour cacher automatiquement toutes les réponses d'une route

    :param ttl: Durée de vie du cache en secondes
    :param key: Clé de cache (facultatif)
    :return: Decorator
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not request.app.debug:
                cached_response = await request.app.ctx.cache.get(request, key)
                if cached_response:
                    cached_response.headers["X-Cache"] = "HIT"
                    cached_response.headers["Cache-Control"] = f"public, max-age={ttl}"
                    cached_response.headers["X-Cache-TTL"] = ttl

                    return cached_response

            response = await func(request, *args, **kwargs)

            if not request.app.debug:
                await request.app.ctx.cache.set(request, response, ttl, key)

            response.headers["X-Cache"] = "MISS"
            response.headers["Cache-Control"] = f"public, max-age={ttl}"
            response.headers["X-Cache-TTL"] = ttl

            return response

        return wrapper

    return decorator
