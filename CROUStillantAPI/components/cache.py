from datetime import datetime


class Cache:
    """
    Classe permettant de gérer un cache de données
    """
    def __init__(self):
        """
        Initialisation du cache
        """
        self.cache = {}
        self.expiration_time = 60 * 5 # 5 minutes
        self.last_check = datetime.now()


    async def get(self, key: str) -> any:
        """
        Récupère une valeur en cache

        :param key: str
        :return: any
        """
        if await self.is_expired(key):
            await self.delete(key)
            return None

        return self.cache.get(key, None)


    async def add(self, key: str, value) -> None:
        """
        Ajoute une valeur en cache

        :param key: str
        :param value: any
        """
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }


    async def delete(self, key: str) -> None:
        """
        Supprime une valeur en cache

        :param key: str
        """
        self.cache.pop(key, None)


    async def is_expired(self, key: str) -> bool:
        """
        Vérifie si une valeur en cache est expirée

        :param key: str
        :return: bool
        """
        if key not in self.cache:
            return True
        else:
            return (datetime.now() - self.cache[key]['timestamp']).seconds >= self.expiration_time


    async def clear(self) -> None:
        """
        Vérifie si certaines valeurs en cache sont expirées, et les supprime le cas échéant
        """
        if (datetime.now() - self.last_check).seconds < 30:
            return

        for key in await self.get_all_keys():
            if await self.is_expired(key):
                await self.delete(key)


    async def get_all_keys(self) -> list[str]:
        """
        Renvoie la liste des clés en cache

        :return: list[str]
        """
        return list(self.cache.keys())
