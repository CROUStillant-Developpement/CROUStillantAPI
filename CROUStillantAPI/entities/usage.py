from asyncpg import Pool, Connection, Record


class Usage:
    """
    Statistiques d'utilisation de l'API, lues dans les tables maintenues de façon
    incrémentale par CROUStillantData (stats_counters, stats_by_route,
    stats_hourly, stats_daily, unique_hashed_ips). Aucune requête ne scanne
    requests_logs.
    """

    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getSummary(self) -> Record:
        """
        Récupère les totaux d'utilisation de l'API depuis le début du suivi.

        :return: Le nombre total de requêtes, de visiteurs uniques et la date de début du suivi
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        (SELECT TOTAL_REQUESTS FROM stats_counters WHERE ID = 1) AS requetes,
                        (SELECT COUNT(*) FROM unique_hashed_ips) AS visiteurs_uniques,
                        (SELECT MIN(DAY) FROM stats_daily) AS depuis
                """,
                timeout=10,
            )

    async def getTopRoutes(self, limit: int = 10) -> list[Record]:
        """
        Récupère les routes publiques les plus appelées.

        Les routes sont normalisées par CROUStillantData (/v1/restaurants/<code>/menu).
        Les routes internes et de service (/v1/interne, /v1/status) sont exclues.

        :param limit: Nombre de routes à récupérer
        :return: Les routes, les plus appelées en premier
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        ROUTE AS route,
                        TOTAL AS requetes,
                        ROUND(SUM_PROCESS_TIME::numeric / NULLIF(COUNT_PROCESS_TIME, 0), 1) AS temps_moyen_ms
                    FROM stats_by_route
                    WHERE ROUTE LIKE '/v1/%'
                      AND ROUTE NOT LIKE '/v1/interne%'
                      AND ROUTE <> '/v1/status'
                    ORDER BY TOTAL DESC
                    LIMIT $1
                """,
                limit,
                timeout=10,
            )

    async def getHistory(self, jours: int) -> list[Record]:
        """
        Récupère l'évolution journalière de l'utilisation de l'API.

        Seuls les jours déjà clôturés par CROUStillantData sont renvoyés (le jour
        en cours est exclu : partiel, il ferait croire à une chute d'activité).

        :param jours: Le nombre de jours d'historique
        :return: Une ligne par jour, du plus ancien au plus récent
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        D.DAY AS jour,
                        H.REQUESTS AS requetes,
                        D.UNIQUE_IPS AS visiteurs_uniques,
                        D.ERRORS_5XX AS erreurs_serveur,
                        ROUND(D.P50_PROCESS_TIME, 1) AS temps_reponse_p50_ms,
                        ROUND(D.P95_PROCESS_TIME, 1) AS temps_reponse_p95_ms
                    FROM stats_daily D
                    LEFT JOIN (
                        SELECT HOUR::date AS DAY, SUM(REQUESTS)::bigint AS REQUESTS
                        FROM stats_hourly
                        WHERE HOUR >= CURRENT_DATE - $1::int
                        GROUP BY 1
                    ) H ON H.DAY = D.DAY
                    WHERE D.DAY >= CURRENT_DATE - $1::int
                    ORDER BY D.DAY
                """,
                jours,
                timeout=10,
            )
