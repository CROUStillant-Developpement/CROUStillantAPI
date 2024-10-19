from asyncpg import Pool, Connection


class Regions:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool


    async def getAll(self) -> list:
        """
        Récupère toutes les régions.

        :return: Les régions
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        *
                    FROM
                        region
                """
            )


    async def getOne(self, id: int) -> dict:
        """
        Récupère une région.

        :param id: ID de la région
        :return: La région
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        *
                    FROM
                        region
                    WHERE
                        idreg = $1
                """,
                id
            )
