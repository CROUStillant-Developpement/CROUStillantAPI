from asyncpg import Pool, Connection


class Taches:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getAll(self) -> list:
        """
        Récupère toutes les tâches.

        :return: Les tâches
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        id
                    FROM
                        tache
                """,
                timeout=5,
            )

    async def getLast(self, limit: int, offset: int) -> list:
        """
        Récupère les dernières tâches.

        :param limit: Nombre de tâches à récupérer
        :param offset: Offset
        :return: Les tâches
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        *
                    FROM
                        tache
                    ORDER BY
                        id DESC
                    LIMIT $1
                    OFFSET $2
                """,
                limit,
                offset,
                timeout=5,
            )

    async def getOne(self, id: int) -> dict:
        """
        Récupère une tâche.

        :param id: ID de la tâche
        :return: La tâche
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        *
                    FROM
                        tache
                    WHERE
                        id = $1
                """,
                id,
                timeout=5,
            )

    async def getRestaurants(self, id: int) -> list:
        """
        Récupère les restaurants d'une tâche.

        :param id: ID de la tâche
        :return: Les restaurants
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        rid
                    FROM
                        tache_log
                    WHERE
                        idtache = $1
                """,
                id,
                timeout=5,
            )

    async def getForRestaurant(self, rid: int, limit: int = 20) -> list:
        """
        Récupère les dernières tâches d'ingestion ayant vérifié un restaurant.

        :param rid: ID du restaurant
        :param limit: Nombre de tâches à récupérer
        :return: Les tâches (id, début, fin) ayant touché ce restaurant, les plus récentes en premier
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        T.id,
                        T.debut,
                        T.fin
                    FROM
                        tache T
                    JOIN tache_log TL ON TL.idtache = T.id
                    WHERE
                        TL.rid = $1
                    ORDER BY
                        T.debut DESC
                    LIMIT $2
                """,
                rid,
                limit,
                timeout=10,
            )
