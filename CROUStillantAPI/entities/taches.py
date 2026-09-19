from asyncpg import Pool, Connection


class Taches:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getAll(self) -> list:
        """
        Récupère toutes les tâches.

        :return: Les tâches
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        id
                    FROM
                        tache
                """,
                timeout=5,
            )

    async def getLast(self, limit: int, offset: int) -> list:
        """
        Récupère les dernières tâches.

        :param limit: Nombre de tâches à récupérer
        :param offset: Offset
        :return: Les tâches
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        *
                    FROM
                        tache
                    ORDER BY
                        id DESC
                    LIMIT $1
                    OFFSET $2
                """,
                limit,
                offset,
                timeout=5,
            )

    async def getOne(self, id: int) -> dict:
        """
        Récupère une tâche.

        :param id: ID de la tâche
        :return: La tâche
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        *
                    FROM
                        tache
                    WHERE
                        id = $1
                """,
                id,
                timeout=5,
            )

    async def getRestaurants(self, id: int) -> list:
        """
        Récupère les restaurants d'une tâche.

        :param id: ID de la tâche
        :return: Les restaurants
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        rid
                    FROM
                        tache_log
                    WHERE
                        idtache = $1
                """,
                id,
                timeout=5,
            )

    async def getSummary(self) -> dict:
        """
        Récupère un résumé de la fraîcheur des données : la dernière tâche lancée,
        la dernière tâche terminée (avec ce qu'elle a ajouté) et l'activité récente.

        :return: Un dictionnaire {derniere, derniere_terminee, recent}
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            derniere = await connection.fetchrow(
                """
                    SELECT id, debut, fin
                    FROM tache
                    ORDER BY debut DESC NULLS LAST
                    LIMIT 1
                """,
                timeout=5,
            )

            derniere_terminee = await connection.fetchrow(
                """
                    SELECT
                        id,
                        debut,
                        fin,
                        ROUND(EXTRACT(EPOCH FROM (fin - debut))::numeric, 1) AS duree,
                        requetes,
                        fin_menus - debut_menus AS nouveaux_menus,
                        fin_repas - debut_repas AS nouveaux_repas,
                        fin_plats - debut_plats AS nouveaux_plats
                    FROM tache
                    WHERE debut IS NOT NULL AND fin IS NOT NULL
                    ORDER BY fin DESC
                    LIMIT 1
                """,
                timeout=5,
            )

            recent = await connection.fetchrow(
                """
                    SELECT
                        COUNT(*) FILTER (WHERE fin >= LOCALTIMESTAMP - INTERVAL '24 hours') AS taches_24h,
                        ROUND(AVG(EXTRACT(EPOCH FROM (fin - debut)))::numeric, 1) AS duree_moyenne_7j
                    FROM tache
                    WHERE debut IS NOT NULL
                      AND fin IS NOT NULL
                      AND fin >= LOCALTIMESTAMP - INTERVAL '7 days'
                """,
                timeout=5,
            )

            return {
                "derniere": derniere,
                "derniere_terminee": derniere_terminee,
                "recent": recent,
            }

    async def getHistory(self, jours: int) -> list:
        """
        Récupère l'évolution journalière des tâches terminées.

        :param jours: Le nombre de jours d'historique
        :return: Une ligne par jour ayant au moins une tâche terminée, du plus ancien au plus récent
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        DATE(fin) AS jour,
                        COUNT(*) AS taches,
                        ROUND(AVG(EXTRACT(EPOCH FROM (fin - debut)))::numeric, 1) AS duree_moyenne,
                        SUM(requetes) AS requetes,
                        SUM(fin_menus - debut_menus) AS nouveaux_menus,
                        SUM(fin_repas - debut_repas) AS nouveaux_repas,
                        SUM(fin_plats - debut_plats) AS nouveaux_plats
                    FROM tache
                    WHERE debut IS NOT NULL
                      AND fin IS NOT NULL
                      AND fin >= CURRENT_DATE - ($1::int - 1)
                    GROUP BY DATE(fin)
                    ORDER BY jour
                """,
                jours,
                timeout=10,
            )

    async def getForRestaurant(self, rid: int, limit: int = 20) -> list:
        """
        Récupère les dernières tâches d'ingestion ayant vérifié un restaurant.

        :param rid: ID du restaurant
        :param limit: Nombre de tâches à récupérer
        :return: Les tâches (id, début, fin) ayant touché ce restaurant, les plus récentes en premier
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        T.id,
                        T.debut,
                        T.fin
                    FROM
                        tache T
                    JOIN tache_log TL ON TL.idtache = T.id
                    WHERE
                        TL.rid = $1
                    ORDER BY
                        T.debut DESC
                    LIMIT $2
                """,
                rid,
                limit,
                timeout=10,
            )
