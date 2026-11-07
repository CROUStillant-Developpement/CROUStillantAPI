from sanic_ext import openapi
from ..components import (
    PlatComponent,
    PlatCanoniqueResumeComponent,
    PlatCanoniqueWithTotalComponent,
    PlatCanoniqueComponent,
    AnalyseResultatComponent,
)


class Plats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=PlatCanoniqueResumeComponent,
        description="Liste des plats canoniques",
    )


class Plat:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = PlatComponent


class PlatsWithTotal:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=PlatCanoniqueWithTotalComponent,
        description="Liste des plats canoniques, du plus servi au moins servi",
    )


class PlatCanonique:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = PlatCanoniqueComponent


class AnalysePlat:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = AnalyseResultatComponent
