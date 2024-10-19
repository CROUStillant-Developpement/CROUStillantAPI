from sanic_ext import openapi
from ..components import RegionComponent


class Regions:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=RegionComponent,
        description="Liste des régions",
    )


class Region:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = RegionComponent
