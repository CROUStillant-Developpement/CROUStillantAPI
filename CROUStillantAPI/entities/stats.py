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
                """,
                timeout=10,
            )

    async def getByRegion(self) -> list:
        """
        Récupère les statistiques agrégées par région (CROUS), à partir de la vue
        matérialisée `v_restaurant_insights_summary` (richesse/variété des menus sur
        l'année scolaire en cours, déjà précalculées par restaurant).

        :return: Les statistiques par région
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        REG.IDREG AS idreg,
                        REG.LIBELLE AS libelle,
                        COUNT(DISTINCT R.RID) AS nb_restaurants,
                        COUNT(DISTINCT R.RID) FILTER (WHERE R.ACTIF) AS nb_restaurants_actifs,
                        COUNT(DISTINCT R.RID) FILTER (WHERE VRIS.nb_repas > 0) AS nb_restaurants_avec_menu,
                        COALESCE(SUM(VRIS.nb_repas), 0)::bigint AS nb_repas,
                        COALESCE(SUM(VRIS.nb_categories), 0)::bigint AS nb_categories,
                        COALESCE(SUM(VRIS.nb_plats), 0)::bigint AS nb_plats,
                        COALESCE(SUM(VRIS.plats_uniques), 0)::bigint AS plats_uniques
                    FROM REGION REG
                    LEFT JOIN RESTAURANT R ON R.IDREG = REG.IDREG
                    LEFT JOIN v_restaurant_insights_summary VRIS ON VRIS.RID = R.RID
                    GROUP BY REG.IDREG, REG.LIBELLE
                    ORDER BY REG.LIBELLE
                """,
                timeout=10,
            )
