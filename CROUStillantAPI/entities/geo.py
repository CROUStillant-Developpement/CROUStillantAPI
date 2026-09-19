from asyncpg import Pool, Connection, Record


class Geo:
    """
    Répartition géographique des visites du site, lue dans GEO_USAGE (sessions
    Umami agrégées par ville par CROUStillantData, voir analytics.py).
    """

    # Nombre minimal de sessions pour qu'une ville soit exposée : une ville avec
    # une ou deux visites permettrait presque d'identifier un utilisateur.
    MIN_SESSIONS = 10

    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getSummary(self) -> Record:
        """
        Récupère les totaux de la répartition géographique.

        :return: Le nombre total de sessions localisées et de villes
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        COALESCE(SUM(TOTAL), 0)::bigint AS sessions,
                        COUNT(*) AS villes
                    FROM GEO_USAGE
                    WHERE TOTAL > 0
                """,
                timeout=10,
            )

    async def getTopCities(self, limit: int = 50) -> list[Record]:
        """
        Récupère les villes d'où le site est le plus consulté.

        :param limit: Nombre de villes à récupérer
        :return: Les villes ayant au moins MIN_SESSIONS sessions, les plus actives en premier
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        GU.CITY AS ville,
                        GD.REGION AS region,
                        GD.COUNTRY_CODE AS pays,
                        GD.LATITUDE AS latitude,
                        GD.LONGITUDE AS longitude,
                        GU.TOTAL AS sessions
                    FROM GEO_USAGE GU
                    JOIN GEO_DATA GD ON GD.CITY = GU.CITY
                    WHERE GU.TOTAL >= $1
                    ORDER BY GU.TOTAL DESC, GU.CITY
                    LIMIT $2
                """,
                self.MIN_SESSIONS,
                limit,
                timeout=10,
            )
