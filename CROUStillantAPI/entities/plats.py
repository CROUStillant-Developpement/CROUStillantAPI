from asyncpg import Pool, Connection


# Analyse d'un plat brut (PLAT, alias P) : à combiner avec PLAT_ANALYSE_JOINS.
# Les composants sont agrégés en JSON, dans l'ordre du libellé (0 = composant principal).
PLAT_ANALYSE_COLUMNS = """
    PA.NATURE,
    PA.TYPE_INFO,
    PA.LIBELLE_NET,
    PA.POINTS::FLOAT8 AS POINTS,
    PA.PRIX::FLOAT8[] AS PRIX,
    PA.ALLERGENES,
    PA.VEGETARIEN,
    PA.ORIGINES,
    PA.LABELS,
    K.COMPOSANTS
"""

PLAT_ANALYSE_JOINS = """
    LEFT JOIN PUBLIC.PLAT_ANALYSE PA ON PA.PLATID = P.PLATID
    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'code', PC.IDPC,
                'libelle', PC.LIBELLE,
                'type', PC.TYPE_PLAT,
                'vegetarien', PC.VEGETARIEN
            ) ORDER BY PCO.ORDRE
        ) AS COMPOSANTS
        FROM PUBLIC.PLAT_COMPOSANT PCO
        JOIN PUBLIC.PLAT_CANONIQUE PC ON PC.IDPC = PCO.IDPC
        WHERE PCO.PLATID = P.PLATID
    ) K ON TRUE
"""


class Plats:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getAll(self) -> list:
        """
        Récupère tous les plats.

        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        platid,
                        libelle
                    FROM
                        plat
                """,
                timeout=10,
            )

    async def getLast(self, limit: int) -> list:
        """
        Récupère les derniers plats canoniques créés (un plat réel, toutes écritures confondues :
        les informations comme « Fermé » ou « Menu non communiqué » n'en sont pas).

        :param limit: Nombre de plats à récupérer
        :return: Les plats canoniques
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        PC.IDPC,
                        PC.LIBELLE,
                        PC.TYPE_PLAT,
                        PC.VEGETARIEN,
                        PC.SOURCE
                    FROM PUBLIC.PLAT_CANONIQUE PC
                    ORDER BY PC.IDPC DESC
                    LIMIT $1
                """,
                limit,
                timeout=5,
            )

    async def getOne(self, id: int) -> dict:
        """
        Récupère un plat, avec son analyse.

        :param id: ID du plat
        :return: Le plat
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                f"""
                    SELECT
                        P.PLATID,
                        P.LIBELLE,
                        {PLAT_ANALYSE_COLUMNS}
                    FROM PUBLIC.PLAT P
                    {PLAT_ANALYSE_JOINS}
                    WHERE P.PLATID = $1
                """,
                id,
                timeout=5,
            )

    async def getTop(self, limit: int = 100, type_restaurant: int = 1) -> list:
        """
        Récupère les plats canoniques les plus servis : chaque libellé brut d'un menu compte pour
        chacun des plats canoniques qu'il contient (« Poisson pané, riz » compte pour le poisson
        pané et pour le riz). Les informations (« Fermé », « Menu non communiqué »...) n'ont pas
        de composant et ne sont donc jamais comptées.

        :param limit: Nombre de plats à récupérer
        :param type_restaurant: Type de restaurant pris en compte (1 = restaurants CROUS)
        :return: Les plats canoniques, avec leur nombre d'occurrences (`nb`)
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        PC.IDPC,
                        PC.LIBELLE,
                        PC.TYPE_PLAT,
                        PC.VEGETARIEN,
                        PC.SOURCE,
                        T.NB
                    FROM (
                        SELECT PCO.IDPC, COUNT(*) AS NB
                        FROM PUBLIC.COMPOSITION CO
                        JOIN PUBLIC.PLAT_COMPOSANT PCO ON PCO.PLATID = CO.PLATID
                        JOIN PUBLIC.CATEGORIE C ON C.CATID = CO.CATID
                        JOIN PUBLIC.REPAS RP ON RP.RPID = C.RPID
                        JOIN PUBLIC.MENU M ON M.MID = RP.MID
                        JOIN PUBLIC.RESTAURANT R ON R.RID = M.RID AND R.IDTPR = $2
                        GROUP BY PCO.IDPC
                        ORDER BY NB DESC
                        LIMIT $1
                    ) T
                    JOIN PUBLIC.PLAT_CANONIQUE PC ON PC.IDPC = T.IDPC
                    ORDER BY T.NB DESC, PC.IDPC
                """,
                limit,
                type_restaurant,
                timeout=30,
            )

    async def getCanonique(self, id: int, variants: int = 20) -> tuple[dict | None, list]:
        """
        Récupère un plat canonique et quelques-uns des libellés bruts qui le désignent.

        :param id: ID du plat canonique
        :param variants: Nombre maximum de libellés bruts à retourner
        :return: Le plat canonique et ses libellés bruts
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            canonique = await connection.fetchrow(
                """
                    SELECT
                        PC.IDPC,
                        PC.LIBELLE,
                        PC.TYPE_PLAT,
                        PC.VEGETARIEN,
                        PC.SOURCE,
                        PC.A_REVOIR,
                        (SELECT COUNT(*) FROM PUBLIC.PLAT_COMPOSANT PCO WHERE PCO.IDPC = PC.IDPC) AS NB_LIBELLES
                    FROM PUBLIC.PLAT_CANONIQUE PC
                    WHERE PC.IDPC = $1
                """,
                id,
                timeout=5,
            )
            if canonique is None:
                return None, []

            libelles = await connection.fetch(
                """
                    SELECT P.PLATID, P.LIBELLE
                    FROM PUBLIC.PLAT_COMPOSANT PCO
                    JOIN PUBLIC.PLAT P ON P.PLATID = PCO.PLATID
                    WHERE PCO.IDPC = $1
                    ORDER BY P.PLATID DESC
                    LIMIT $2
                """,
                id,
                variants,
                timeout=5,
            )

            return canonique, libelles

    async def getCanoniquesByKeys(self, keys: list[str]) -> dict[str, dict]:
        """
        Récupère les plats canoniques correspondant à des clés (croustillant_classifier).

        :param keys: Les clés canoniques
        :return: Les plats canoniques, indexés par clé
        """
        if not keys:
            return {}

        async with self.pool.acquire() as connection:
            connection: Connection

            rows = await connection.fetch(
                """
                    SELECT IDPC, CLE, LIBELLE, TYPE_PLAT, VEGETARIEN, CONFIANCE, SOURCE, A_REVOIR
                    FROM PUBLIC.PLAT_CANONIQUE
                    WHERE CLE = ANY($1::VARCHAR[])
                """,
                keys,
                timeout=5,
            )

            return {row.get("cle"): row for row in rows}
