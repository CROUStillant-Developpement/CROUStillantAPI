from asyncpg import Pool, Connection
from datetime import datetime


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

            return await connection.fetch(
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
                timeout=10,
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

            return await connection.fetch(
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
                timeout=10,
            )

    async def getDates(self, id: int) -> dict:
        """
        Récupère les dates des prochains menus d'un restaurant.

        :param id: ID du restaurant
        :return: Les dates des menus
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
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

            return await connection.fetch(
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
