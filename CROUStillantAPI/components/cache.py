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
        if self.is_expired(key):
            self.delete(key)
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


    async def clear(self) -> None:
        """
        Vide le cache
        """
        self.cache.clear()


    async def is_expired(self, key: str) -> bool:
        """
        Vérifie si une valeur en cache est expirée

        :param key: str
        :return: bool
        """
        if key not in self.cache:
            return True

        timestamp = self.cache[key]['timestamp']
        return (datetime.now() - timestamp).seconds >= self.expiration_time


    async def check(self) -> None:
        """
        Vérifie si certaines valeurs en cache sont expirées, et les supprime le cas échéant
        """
        if (datetime.now() - self.last_check).seconds < 30:
            return

        for key in self.cache.keys():
            if self.is_expired(key):
                self.delete(key)


    async def get_all_keys(self) -> list[str]:
        """
        Renvoie la liste des clés en cache

        :return: list[str]
        """
        return self.cache.keys()
