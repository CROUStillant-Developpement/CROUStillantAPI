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
                        *
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
                        *
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
                        *
                    FROM
                        plat
                    WHERE
                        platid = $1
                """,
                id,
                timeout=5,
            )

    async def getTop(self, limit: int = 100, type_restaurant: int = 1) -> dict:
        """
        Récupère les plats les plus populaires.

        :param limit: Nombre de plats à récupérer
        :param type_restaurant: Type de restaurant (idtpr)
        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        P.platid,
                        P.libelle,
                        COUNT(C.platid) AS nb
                    FROM
                        plat P
                    JOIN composition C ON P.platid = C.platid
                    JOIN categorie c2 ON c2.catid = C.catid
                    JOIN repas R ON c2.rpid = R.rpid
                    JOIN menu M ON R.mid = M.mid
                    JOIN restaurant R2 ON M.rid = R2.rid AND R2.idtpr = $2
                    GROUP BY
                        P.platid
                    ORDER BY
                        nb DESC
                    LIMIT $1
                """,
                limit,
                type_restaurant,
                timeout=15,
            )
