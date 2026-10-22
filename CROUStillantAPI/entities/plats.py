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
        Récupère les derniers plats, avec leur analyse.

        :param limit: Nombre de plats à récupérer
        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                f"""
                    SELECT
                        P.PLATID,
                        P.LIBELLE,
                        {PLAT_ANALYSE_COLUMNS}
                    FROM PUBLIC.PLAT P
                    {PLAT_ANALYSE_JOINS}
                    ORDER BY P.PLATID DESC
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
        Récupère les plats les plus populaires, depuis la vue matérialisée `v_plats_top`
        (précalculée pour type_restaurant = 1 et rafraîchie à chaque cycle d'ingestion,
        voir `CROUStillant/__main__.py`).

        :param limit: Nombre de plats à récupérer (parmi les 100 précalculés)
        :param type_restaurant: Non utilisé : la vue ne précalcule que le type_restaurant = 1
        :return: Les plats
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetch(
                """
                    SELECT
                        platid,
                        libelle,
                        nb
                    FROM v_plats_top
                    ORDER BY rang
                    LIMIT $1
                """,
                limit,
                timeout=5,
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
