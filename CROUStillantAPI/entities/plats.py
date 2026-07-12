from asyncpg import Pool, Connection


class Plats:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getAll(self) -> list:
        """
        Récupère tous les plats.

        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        platid,
                        libelle
                    FROM
                        plat
                """,
                timeout=10,
            )

    async def getLast(self, limit: int) -> list:
        """
        Récupère les derniers plats.

        :param limit: Nombre de plats à récupérer
        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        platid,
                        libelle
                    FROM
                        plat
                    ORDER BY
                        platid DESC
                    LIMIT $1
                """,
                limit,
                timeout=5,
            )

    async def getOne(self, id: int) -> dict:
        """
        Récupère un plat.

        :param id: ID du plat
        :return: Le plat
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        platid,
                        libelle
                    FROM
                        plat
                    WHERE
                        platid = $1
                """,
                id,
                timeout=5,
            )

    async def getTop(self, limit: int = 100, type_restaurant: int = 1) -> list:
        """
        Récupère les plats les plus populaires, depuis la vue matérialisée `v_plats_top`
        (précalculée pour type_restaurant = 1 et rafraîchie à chaque cycle d'ingestion,
        voir `CROUStillant/__main__.py`).

        :param limit: Nombre de plats à récupérer (parmi les 100 précalculés)
        :param type_restaurant: Non utilisé : la vue ne précalcule que le type_restaurant = 1
        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        platid,
                        libelle,
                        nb
                    FROM v_plats_top
                    ORDER BY rang
                    LIMIT $1
                """,
                limit,
                timeout=5,
            )

