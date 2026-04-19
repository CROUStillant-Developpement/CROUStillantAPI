from asyncpg import Pool, Connection


class Restaurants:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def getAll(
        self,
        actif: bool = True,
        ouvert: bool | None = None,
        region: int | None = None,
        type_: int | None = None,
        ispmr: bool | None = None,
        zone: str | None = None,
    ) -> list:
        """
        Récupère tous les restaurants.

        :return: Les restaurants
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            conditions = []
            params = []

            if actif:
                conditions.append("ACTIF = TRUE")
            if ouvert is not None:
                conditions.append(f"OPENED = {'TRUE' if ouvert else 'FALSE'}")
            if ispmr is not None:
                conditions.append(f"ISPMR = {'TRUE' if ispmr else 'FALSE'}")
            if region is not None:
                params.append(region)
                conditions.append(f"R.IDREG = ${len(params)}")
            if type_ is not None:
                params.append(type_)
                conditions.append(f"TPR.IDTPR = ${len(params)}")
            if zone is not None:
                params.append(zone)
                conditions.append(f"ZONE ILIKE ${len(params)}")

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            return await connection.fetch(
                f"""
                    SELECT
                        RID,
                        R.IDREG AS IDREG,
                        R.LIBELLE AS REGION,
                        TPR.IDTPR AS IDTPR,
                        TPR.LIBELLE AS TYPE,
                        NOM,
                        ADRESSE,
                        LATITUDE,
                        LONGITUDE,
                        HORAIRES,
                        JOURS_OUVERT,
                        CASE
                            WHEN IMAGE_URL IS NULL THEN NULL
                            ELSE CONCAT('https://api.croustillant.menu/v1/restaurants/', RID, '/preview')
                        END AS IMAGE_URL,
                        EMAIL,
                        TELEPHONE,
                        ISPMR,
                        ZONE,
                        (PAIEMENT::jsonb - 'Carte bancaire') AS PAIEMENT,
                        ACCES,
                        OPENED,
                        ACTIF
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    {where_clause}
                """,
                *params,
            )

    async def getStatus(self, ouvert: bool | None = None) -> list:
        """
        Récupère le statut d'ouverture de tous les restaurants actifs.

        :return: Les restaurants avec leur statut
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            conditions = ["ACTIF = TRUE"]
            if ouvert is not None:
                conditions.append(f"OPENED = {'TRUE' if ouvert else 'FALSE'}")

            where_clause = f"WHERE {' AND '.join(conditions)}"

            return await connection.fetch(
                f"""
                    SELECT
                        RID,
                        R.IDREG AS IDREG,
                        R.LIBELLE AS REGION,
                        TPR.IDTPR AS IDTPR,
                        TPR.LIBELLE AS TYPE,
                        NOM,
                        OPENED,
                        ACTIF
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    {where_clause}
                """
            )

    async def getOne(self, id: int) -> dict:
        """
        Récupère un restaurant.

        :param id: ID du restaurant
        :return: Le restaurant
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        RID,
                        R.IDREG AS IDREG,
                        R.LIBELLE AS REGION,
                        TPR.IDTPR AS IDTPR,
                        TPR.LIBELLE AS TYPE,
                        NOM,
                        ADRESSE,
                        LATITUDE,
                        LONGITUDE,
                        HORAIRES,
                        JOURS_OUVERT,
                        CASE 
                            WHEN IMAGE_URL IS NULL THEN NULL
                            ELSE CONCAT('https://api.croustillant.menu/v1/restaurants/', RID, '/preview')
                        END AS IMAGE_URL,
                        EMAIL,
                        TELEPHONE,
                        ISPMR,
                        ZONE,
                        (PAIEMENT::jsonb - 'Carte bancaire') AS PAIEMENT,
                        ACCES,
                        OPENED,
                        ACTIF
                    FROM
                        restaurant
                    JOIN region R ON restaurant.idreg = R.idreg
                    JOIN type_restaurant TPR ON restaurant.idtpr = TPR.idtpr
                    WHERE
                        rid = $1
                """,
                id,
            )

    async def getInfo(self, id: int) -> dict:
        """
        Récupère un restaurant.

        :param id: ID du restaurant
        :return: Le restaurant
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        R.RID,
                        R.AJOUT AS AJOUT,
                        R.MIS_A_JOUR AS MODIFIE,
                        (SELECT COUNT(*) FROM tache_log WHERE rid = $1) AS TACHES
                    FROM
                        restaurant R
                    WHERE
                        R.RID = $1
                """,
                id,
            )

    async def getPreview(self, id: int) -> dict:
        """
        Récupère un aperçu d'un restaurant.

        :param id: ID du restaurant
        :return: L'aperçu du restaurant
        """
        async with self.pool.acquire() as connection:
            connection: Connection

            return await connection.fetchrow(
                """
                    SELECT
                        NOM,
                        R.IMAGE_URL,
                        RAW_IMAGE
                    FROM
                        RESTAURANT_IMAGE
                    JOIN RESTAURANT R ON RESTAURANT_IMAGE.IMAGE_URL = R.IMAGE_URL
                    WHERE
                        R.RID = $1
                """,
                id,
            )
