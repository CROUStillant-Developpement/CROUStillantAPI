from asyncpg import Pool, Connection
from datetime import datetime
import asyncio


async def _fetch(connection: Connection, query: str, *args, timeout: int, retries: int = 1):
    """
    Effectue une requête avec un timeout et des tentatives de retry en cas de timeout.
    
    :param connection: La connexion à la base de données
    :type connection: Connection
    :param query: La requête SQL à exécuter
    :type query: str
    :param args: Les arguments de la requête
    :type args: list
    :param timeout: Le temps maximum en secondes pour attendre la réponse de la base de données
    :type timeout: int
    :param retries: Le nombre de tentatives de retry en cas de timeout
    :type retries: int
    :return: Le résultat de la requête
    :rtype: list
    :raises TimeoutError: Si la requête dépasse le temps imparti après les tentatives de retry
    """

    for attempt in range(retries + 1):
        try:
            return await connection.fetch(query, *args, timeout=timeout)
        except TimeoutError:
            if attempt < retries:
                await asyncio.sleep(0.5)
                continue
            raise


class Menus:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getCurrent(self, id: int, date: datetime) -> dict:
        """
        Récupère le menu d'un restaurant.

        :param id: ID du restaurant
        :param date: Date du menu
        :return: Le menu
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await _fetch(
                connection,
                """
                    WITH LatestMenus AS (
                        SELECT DISTINCT ON (M.DATE)
                            M.MID,
                            M.DATE
                        FROM PUBLIC.MENU M
                        WHERE M.RID = $1
                        AND M.DATE >= $2
                        ORDER BY M.DATE, M.MID DESC
                    )

                    SELECT
                        M.MID,
                        M.DATE,
                        RP.RPID,
                        RP.TPR,
                        C.CATID,
                        C.TPCAT,
                        C.ORDRE AS CAT_ORDRE,
                        P.PLATID,
                        P.LIBELLE AS PLAT,
                        CO.ORDRE AS PLAT_ORDRE
                    FROM PUBLIC.MENU M
                    JOIN LatestMenus LM ON M.MID = LM.MID
                    JOIN PUBLIC.REPAS RP ON M.MID = RP.MID
                    JOIN PUBLIC.CATEGORIE C ON RP.RPID = C.RPID
                    LEFT JOIN PUBLIC.COMPOSITION CO ON C.CATID = CO.CATID
                    LEFT JOIN PUBLIC.PLAT P ON CO.PLATID = P.PLATID
                    ORDER BY M.DATE, RP.RPID, C.ORDRE, CO.ORDRE
                """,
                id,
                date,
                timeout=8,
            )

    async def getFromDate(self, id: int, date: datetime) -> dict:
        """
        Récupère le menu d'un restaurant.

        :param id: ID du restaurant
        :param date: Date du menu
        :return: Le menu
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await _fetch(
                connection,
                """
                    WITH LatestMenu AS (
                        SELECT MAX(MID) AS MID
                        FROM PUBLIC.MENU
                        WHERE RID = $1 AND DATE = $2
                    )

                    SELECT
                        M.MID,
                        M.DATE,
                        RP.RPID,
                        RP.TPR,
                        C.CATID,
                        C.TPCAT,
                        C.ORDRE AS CAT_ORDRE,
                        P.PLATID,
                        P.LIBELLE AS PLAT,
                        CO.ORDRE AS PLAT_ORDRE
                    FROM PUBLIC.MENU M
                    JOIN LatestMenu LM ON M.MID = LM.MID
                    JOIN PUBLIC.REPAS RP ON M.MID = RP.MID
                    JOIN PUBLIC.CATEGORIE C ON RP.RPID = C.RPID
                    LEFT JOIN PUBLIC.COMPOSITION CO ON C.CATID = CO.CATID
                    LEFT JOIN PUBLIC.PLAT P ON CO.PLATID = P.PLATID
                    ORDER BY RP.RPID, C.ORDRE, CO.ORDRE
                """,
                id,
                date,
                timeout=8,
            )

    async def getDates(self, id: int) -> dict:
        """
        Récupère les dates des prochains menus d'un restaurant.

        :param id: ID du restaurant
        :return: Les dates des menus
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await _fetch(
                connection,
                """
                    SELECT DISTINCT ON (M.DATE)
                        M.MID,
                        M.DATE
                    FROM PUBLIC.MENU M
                    JOIN PUBLIC.RESTAURANT R ON M.RID = R.RID
                    WHERE R.RID = $1
                    AND M.DATE >= CURRENT_DATE
                    ORDER BY M.DATE, M.MID DESC
                """,
                id,
                timeout=5,
            )

    async def getAllDates(self, id: int) -> dict:
        """
        Récupère les dates des menus d'un restaurant.

        :param id: ID du restaurant
        :return: Les dates des menus
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await _fetch(
                connection,
                """
                    SELECT DISTINCT ON (M.DATE)
                        M.MID,
                        M.DATE
                    FROM PUBLIC.MENU M
                    JOIN PUBLIC.RESTAURANT R ON M.RID = R.RID
                    WHERE R.RID = $1
                    ORDER BY M.DATE, M.MID DESC
                """,
                id,
                timeout=5,
            )

    async def getFirstDate(self, id: int) -> dict:
        """
        Récupère la date du premier menu connu d'un restaurant.

        :param id: ID du restaurant
        :return: La date du premier menu (ou None si aucun menu)
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT MIN(DATE) AS DATE
                    FROM PUBLIC.MENU
                    WHERE RID = $1
                """,
                id,
                timeout=5,
            )

    async def getDatesInRange(self, id: int, date_from: datetime, date_to: datetime) -> list:
        """
        Récupère les dates des menus d'un restaurant sur une période donnée.

        :param id: ID du restaurant
        :param date_from: Date de début de la période
        :param date_to: Date de fin de la période
        :return: Les dates des menus sur la période
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT DISTINCT M.DATE
                    FROM PUBLIC.MENU M
                    WHERE M.RID = $1
                    AND M.DATE BETWEEN $2 AND $3
                """,
                id,
                date_from,
                date_to,
                timeout=10,
            )

    async def getRepasBreakdown(self, id: int, date_from: datetime, date_to: datetime) -> list:
        """
        Récupère la répartition des repas (matin/midi/soir) d'un restaurant sur une période donnée.

        :param id: ID du restaurant
        :param date_from: Date de début de la période
        :param date_to: Date de fin de la période
        :return: La répartition des repas
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT RP.TPR, COUNT(*) AS NB
                    FROM PUBLIC.REPAS RP
                    JOIN PUBLIC.MENU M ON RP.MID = M.MID
                    WHERE M.RID = $1
                    AND M.DATE BETWEEN $2 AND $3
                    GROUP BY RP.TPR
                """,
                id,
                date_from,
                date_to,
                timeout=10,
            )

    async def getPublishLag(self, id: int, date_from: datetime, date_to: datetime) -> dict:
        """
        Récupère le délai moyen (en jours) entre l'ingestion d'un menu et la date à laquelle il s'applique.

        Une valeur positive signifie que le menu est en moyenne ingéré avant la date du menu (publication à l'avance).

        :param id: ID du restaurant
        :param date_from: Date de début de la période
        :param date_to: Date de fin de la période
        :return: Le délai moyen en jours
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT AVG(M.DATE - M.INGESTION_AT::date) AS MOYENNE_JOURS
                    FROM PUBLIC.MENU M
                    WHERE M.RID = $1
                    AND M.DATE BETWEEN $2 AND $3
                """,
                id,
                date_from,
                date_to,
                timeout=10,
            )

    async def getRegionAverageMenuDays(
        self, idreg: int, exclude_rid: int, date_from: datetime, date_to: datetime
    ) -> dict:
        """
        Récupère la moyenne du nombre de jours avec un menu publié pour les autres restaurants actifs de la même région, sur une période donnée.

        :param idreg: ID de la région
        :param exclude_rid: ID du restaurant à exclure de la comparaison
        :param date_from: Date de début de la période
        :param date_to: Date de fin de la période
        :return: La moyenne de jours avec menu et le nombre de restaurants comparés
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        AVG(SUB.NB) AS MOYENNE,
                        COUNT(*) AS NB_RESTAURANTS,
                        (
                            SELECT COUNT(*)
                            FROM PUBLIC.RESTAURANT R2
                            WHERE R2.IDREG = $1
                            AND R2.ACTIF = TRUE
                            AND R2.RID != $2
                        ) AS NB_RESTAURANTS_ACTIFS
                    FROM (
                        SELECT M.RID, COUNT(DISTINCT M.DATE) AS NB
                        FROM PUBLIC.MENU M
                        JOIN PUBLIC.RESTAURANT R ON M.RID = R.RID
                        WHERE R.IDREG = $1
                        AND R.ACTIF = TRUE
                        AND R.RID != $2
                        AND M.DATE BETWEEN $3 AND $4
                        GROUP BY M.RID
                    ) SUB
                """,
                idreg,
                exclude_rid,
                date_from,
                date_to,
                timeout=15,
            )
