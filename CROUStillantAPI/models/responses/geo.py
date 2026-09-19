from sanic_ext import openapi


class GeoCity:
    ville = openapi.String(
        description="Ville",
        example="Lyon",
    )
    region = openapi.String(
        description="Région",
        example="Auvergne-Rhône-Alpes",
    )
    pays = openapi.String(
        description="Code pays (ISO 3166-1 alpha-2)",
        example="FR",
    )
    latitude = openapi.Float(
        description="Latitude",
        example=45.764,
    )
    longitude = openapi.Float(
        description="Longitude",
        example=4.8357,
    )
    sessions = openapi.Integer(
        description="Nombre de sessions sur le site depuis cette ville",
        example=5200,
    )


class GeoStatsData:
    sessions = openapi.Integer(
        description="Nombre total de sessions localisées sur le site",
        example=180000,
    )
    villes = openapi.Integer(
        description="Nombre total de villes d'où le site a été consulté",
        example=2400,
    )
    top = openapi.Array(
        items=GeoCity,
        description="Les 50 villes les plus actives (au moins 10 sessions)",
    )


class GeoStats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = GeoStatsData
