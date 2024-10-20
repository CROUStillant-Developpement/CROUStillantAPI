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
                    JOIN PUBLIC.RESTAURANT R ON M.RID = R.RID
                    JOIN PUBLIC.REPAS RP ON M.MID = RP.MID
                    JOIN PUBLIC.CATEGORIE C ON RP.RPID = C.RPID
                    JOIN PUBLIC.COMPOSITION CO ON C.CATID = CO.CATID
                    JOIN PUBLIC.PLAT P ON CO.PLATID = P.PLATID
                    WHERE R.RID = $1 AND M.DATE >= $2
                    ORDER BY M.DATE, RP.RPID, C.ORDRE, CO.ORDRE
                """,
                id,
                date
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
                    JOIN PUBLIC.RESTAURANT R ON M.RID = R.RID
                    JOIN PUBLIC.REPAS RP ON M.MID = RP.MID
                    JOIN PUBLIC.CATEGORIE C ON RP.RPID = C.RPID
                    JOIN PUBLIC.COMPOSITION CO ON C.CATID = CO.CATID
                    JOIN PUBLIC.PLAT P ON CO.PLATID = P.PLATID
                    WHERE R.RID = $1 AND M.DATE = $2
                    ORDER BY M.DATE, RP.RPID, C.ORDRE, CO.ORDRE
                """,
                id,
                date
            )
