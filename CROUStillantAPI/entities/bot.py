from asyncpg import Pool, Connection, Record


class Bot:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getLatest(self) -> Record | None:
        """
        Récupère le dernier relevé du bot Discord (table bot_stats, alimentée par
        CROUStillantData toutes les 5 minutes).

        Le statut et la latence sont ceux du dernier relevé, les compteurs ceux du
        dernier relevé où le bot était joignable (un relevé 'offline' n'en a pas).
        La disponibilité est la part des relevés online/degraded sur la période.

        :return: Le dernier relevé, ou None si aucun relevé n'existe
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    WITH dernier AS (
                        SELECT CREATED_AT, STATUS, LATENCY_MS
                        FROM bot_stats
                        ORDER BY CREATED_AT DESC
                        LIMIT 1
                    ), compteurs AS (
                        SELECT GUILDS, USERS, CHANNELS, SHARDS
                        FROM bot_stats
                        WHERE GUILDS IS NOT NULL
                        ORDER BY CREATED_AT DESC
                        LIMIT 1
                    )
                    SELECT
                        dernier.CREATED_AT AS date,
                        dernier.STATUS AS statut,
                        dernier.LATENCY_MS AS latence_ms,
                        compteurs.GUILDS AS serveurs,
                        compteurs.USERS AS utilisateurs,
                        compteurs.CHANNELS AS salons,
                        compteurs.SHARDS AS shards,
                        (
                            SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE STATUS IN ('online', 'degraded')) / NULLIF(COUNT(*), 0), 2)
                            FROM bot_stats
                            WHERE CREATED_AT >= NOW() - INTERVAL '24 hours'
                        ) AS disponibilite_24h,
                        (
                            SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE STATUS IN ('online', 'degraded')) / NULLIF(COUNT(*), 0), 2)
                            FROM bot_stats
                            WHERE CREATED_AT >= NOW() - INTERVAL '30 days'
                        ) AS disponibilite_30j
                    FROM dernier
                    LEFT JOIN compteurs ON TRUE
                """,
                timeout=10,
            )

    async def getHistory(self, jours: int) -> list[Record]:
        """
        Récupère l'évolution journalière des statistiques du bot Discord (vue
        matérialisée bot_stats_daily, rafraîchie par CROUStillantData).

        :param jours: Le nombre de jours d'historique
        :return: Une ligne par jour, du plus ancien au plus récent
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        day AS jour,
                        guilds AS serveurs,
                        users AS utilisateurs,
                        channels AS salons,
                        shards,
                        latency_ms AS latence_ms,
                        uptime AS disponibilite,
                        samples AS releves
                    FROM bot_stats_daily
                    WHERE day > (NOW() AT TIME ZONE 'Europe/Paris')::date - $1::int
                    ORDER BY day
                """,
                jours,
                timeout=10,
            )
