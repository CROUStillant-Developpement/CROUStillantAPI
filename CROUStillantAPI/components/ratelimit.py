import binascii
import functools
import time

from ..exceptions.ratelimit import RatelimitException
from sanic.request import Request
from sanic.response import HTTPResponse
from asyncpg import Pool


class Bucket:
    """
    Classe représentant un bucket de rate limiting

    :param ident: Identifiant du bucket
    :param limit: Nombre de requêtes autorisées
    :param secs: Durée du bucket
    """
    def __init__(self, ident: str, limit: int, secs: int) -> None:
        self.ident = binascii.crc32(ident.encode())
        self.limit = limit
        self.secs = secs


class Ratelimiter:
    """
    Classe permettant de gérer les rate limits
    """
    def __init__(self) -> None:
        """
        Initialisation de la classe
        """
        self.ratelimits = {}
        self.last_ratelimit_cleanup = int(time.time())

        self.cache_buckets = {}
        self.cache_refresh = 300
        self.DEFAULT = Bucket("default", 200, 60)


    async def check_ratelimit(self, key: str, bucket: Bucket) -> dict:
        """
        Vérifie si une requête est autorisée
        
        :param key: Clé de la requête
        :param bucket: Bucket de rate limiting
        :return: Headers de la requête
        """
        await self.cleanup()

        current_time = int(time.time())
        self.ratelimits.setdefault(key, {})

        window_start = current_time // bucket.secs * bucket.secs

        self.ratelimits[key].setdefault(bucket.ident, {
            'remaining': bucket.limit,
            'reset': window_start + bucket.secs,
            'window_start': window_start,
        })

        bucket_data = self.ratelimits[key][bucket.ident]

        if current_time >= bucket_data['reset']:
            bucket_data['remaining'] = bucket.limit
            bucket_data['reset'] = window_start + bucket.secs
            bucket_data['window_start'] = window_start

        bucket_data['remaining'] -= 1

        headers = {
            'X-RateLimit-Limit': bucket.limit,
            'X-RateLimit-Remaining': max(bucket_data['remaining'], 0),
            'X-RateLimit-Reset': bucket_data['reset'] - current_time,  # Time remaining to reset
            'X-RateLimit-Bucket': bucket.ident,
            'X-RateLimit-Used': bucket.limit - bucket_data['remaining'],
            'X-RateLimit-Key': key,
        }

        if bucket_data['remaining'] < 0:
            headers.update({'Retry-After': bucket_data['reset'] - current_time})
            raise RatelimitException(
                headers=headers,
                extra={'cooldown': bucket_data['reset'] - current_time}
            )

        return headers


    async def cleanup(self) -> None:
        """
        Nettoie les rate limits expirées afin de libérer de la mémoire
        """
        current_time = int(time.time())

        if current_time - self.last_ratelimit_cleanup < 60:
            return

        for key, buckets in self.ratelimits.items():
            for bucket, data in list(buckets.items()):
                if data['reset'] < current_time:
                    del self.ratelimits[key][bucket]

        self.last_ratelimit_cleanup = current_time


    async def getBucket(self, pool: Pool, key: str) -> Bucket:
        """
        Récupère un bucket, soit depuis le cache, soit depuis la base de données si le cache est expiré ou inexistant.
        Permet de limiter les requêtes à la base de données et avoir des buckets dynamiques.

        :param pool: Pool de connexions à la base de données
        :param key: Clé de la requête (IP)
        :return: Bucket
        """
        if key in self.cache_buckets and self.cache_buckets[key]["expires"] > int(time.time()):
            return self.cache_buckets[key]["bucket"]
        else:
            async with pool.acquire() as connection:
                data = await connection.fetchrow("SELECT * FROM buckets WHERE key = $1", key)

            if data is None:
                self.cache_buckets[key] = self.DEFAULT

                return self.DEFAULT

            bucket = Bucket(data["key"], data["limit"], data["secs"])
            self.cache_buckets[key] = {
                "expires": int(time.time()) + self.cache_refresh,
                "bucket": bucket
            }

            return bucket


def ratelimit():
    """
    Décorateur permettant de limiter le nombre de requêtes par seconde
    """
    def wrapper(func) -> callable:
        """
        Fonction interne du décorateur
        
        :param func: Fonction à décorer
        :return: Fonction décorée
        """
        @functools.wraps(func)
        async def wrapped(request: Request, *args, **kwargs) -> HTTPResponse:
            """
            Fonction interne du décorateur
            
            :param request: Requête
            :param args: Arguments
            :param kwargs: Arguments nommés
            :return: Réponse
            """
            key = request.client_ip

            ratelimiter: Ratelimiter = request.app.ctx.ratelimiter

            bucket: Bucket = await ratelimiter.getBucket(request.app.pool, key)

            headers = await ratelimiter.check_ratelimit(key, bucket)

            resp: HTTPResponse = await func(request, *args, **kwargs)
            resp.headers.update(headers)

            return resp
        return wrapped
    return wrapper
