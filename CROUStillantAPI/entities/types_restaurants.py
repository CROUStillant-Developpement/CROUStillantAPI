from asyncpg import Pool, Connection


class TypesRestaurants:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool


    async def getAll(self) -> list:
        """
        Récupère tous les types des restaurants.

        :return: Les types des restaurants
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT *
                    FROM
                        type_restaurant
                """
            )
