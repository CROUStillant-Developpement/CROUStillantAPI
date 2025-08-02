from asyncpg import Pool, Connection


class Stats:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool


    async def get(self) -> list:
        """
        Récupère toutes les statistiques.

        :return: Les statistiques.
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT * FROM v_stats;
                """
            )
