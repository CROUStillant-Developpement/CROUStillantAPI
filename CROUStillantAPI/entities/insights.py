from asyncpg import Pool, Connection


class Insights:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getSummary(self, rid: int) -> dict:
        """
        Récupère le résumé pré-calculé des insights d'un restaurant (richesse, variété,
        plats fréquents) depuis la vue matérialisée `v_restaurant_insights_summary`.

        Voir `CROUStillant/__main__.py` pour le rafraîchissement périodique de cette vue.

        :param rid: ID du restaurant
        :return: Le résumé des insights (ou None si le restaurant n'est pas actif/n'a pas de menu)
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        rid,
                        periode_debut,
                        periode_fin,
                        nb_repas,
                        nb_categories,
                        nb_plats,
                        plats_uniques,
                        plats_frequents
                    FROM v_restaurant_insights_summary
                    WHERE rid = $1
                """,
                rid,
                timeout=5,
            )
