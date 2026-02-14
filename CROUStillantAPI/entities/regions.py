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
                id,
            )

    async def getRestaurants(self, id: int) -> list[dict]:
        """
        Récupère les restaurants d'une région.

        :param id: ID de la région
        :return: Les restaurants
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        RID,
                        R.IDREG AS IDREG,
                        R.LIBELLE AS REGION,
                        TPR.IDTPR AS IDTPR,
                        TPR.LIBELLE AS TYPE,
                        NOM,
                        ADRESSE,
                        LATITUDE,
                        LONGITUDE,
                        HORAIRES,
                        JOURS_OUVERT,
                        CASE 
                            WHEN IMAGE_URL IS NULL THEN NULL
                            ELSE CONCAT('https://api.croustillant.menu/v1/restaurants/', RID, '/preview')
                        END AS IMAGE_URL,
                        EMAIL,
                        TELEPHONE,
                        ISPMR,
                        ZONE,
                        PAIEMENT,
                        ACCES,
                        OPENED
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    WHERE
                        restaurant.idreg = $1
                """,
                id,
            )
