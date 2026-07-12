from asyncpg import Pool, Connection
from datetime import datetime


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

    async def getTopForRestaurant(
        self, id: int, date_from: datetime, date_to: datetime, limit: int = 10
    ) -> list:
        """
        Récupère les plats les plus fréquents d'un restaurant sur une période donnée.

        :param id: ID du restaurant
        :param date_from: Date de début de la période
        :param date_to: Date de fin de la période
        :param limit: Nombre de plats à récupérer
        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        P.platid,
                        P.libelle,
                        COUNT(*) AS nb
                    FROM
                        plat P
                    JOIN composition CO ON P.platid = CO.platid
                    JOIN categorie C ON CO.catid = C.catid
                    JOIN repas RP ON C.rpid = RP.rpid
                    JOIN menu M ON RP.mid = M.mid
                    WHERE
                        M.rid = $1
                        AND M.date BETWEEN $2 AND $3
                    GROUP BY
                        P.platid, P.libelle
                    ORDER BY
                        nb DESC
                    LIMIT $4
                """,
                id,
                date_from,
                date_to,
                limit,
                timeout=15,
            )

    async def getVariety(self, id: int, date_from: datetime, date_to: datetime) -> dict:
        """
        Récupère la variété des plats d'un restaurant sur une période donnée (plats uniques vs total des plats servis).

        :param id: ID du restaurant
        :param date_from: Date de début de la période
        :param date_to: Date de fin de la période
        :return: Le nombre de plats uniques et le nombre total de plats servis
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        COUNT(DISTINCT P.platid) AS plats_uniques,
                        COUNT(*) AS plats_total
                    FROM
                        plat P
                    JOIN composition CO ON P.platid = CO.platid
                    JOIN categorie C ON CO.catid = C.catid
                    JOIN repas RP ON C.rpid = RP.rpid
                    JOIN menu M ON RP.mid = M.mid
                    WHERE
                        M.rid = $1
                        AND M.date BETWEEN $2 AND $3
                """,
                id,
                date_from,
                date_to,
                timeout=15,
            )
