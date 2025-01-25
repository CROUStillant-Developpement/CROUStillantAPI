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

            # return await connection.fetchrow(
            #     """
            #         SELECT
            #             (SELECT COUNT(*) FROM REGION) AS regions,
            #             (SELECT COUNT(*) FROM RESTAURANT) AS restaurants,
            #             (SELECT COUNT(*) FROM TYPE_RESTAURANT) AS types_restaurants,
            #             (SELECT COUNT(*) FROM MENU) AS menus,
            #             (SELECT COUNT(*) FROM REPAS) AS repas,
            #             (SELECT COUNT(*) FROM CATEGORIE) AS categories,
            #             (SELECT COUNT(*) FROM PLAT) AS plats,
            #             (SELECT COUNT(*) FROM COMPOSITION) AS compositions
            #     """
            # )

            # Pour des raisons de performances, on récupère les statistiques depuis la dernière tâche au lieu de les calculer à chaque fois
            return await connection.fetchrow(
                """
                    SELECT
                        FIN_REGIONS AS regions,
                        FIN_RESTAURANTS AS restaurants,
                        FIN_ACTIFS AS restaurants_actifs,
                        FIN_TYPES_RESTAURANTS AS types_restaurants,
                        FIN_MENUS AS menus,
                        FIN_REPAS AS repas,
                        FIN_CATEGORIES AS categories,
                        FIN_PLATS AS plats,
                        FIN_COMPOSITIONS AS compositions
                    FROM TACHE
                    ORDER BY ID DESC
                    LIMIT 1
                """
            )
