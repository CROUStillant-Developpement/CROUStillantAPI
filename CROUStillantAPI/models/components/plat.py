from sanic_ext import openapi


@openapi.component
class Plat:
    code = openapi.String(
        description="Identifiant du plat",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé du plat",
        example="Dinde provençal",
    )


@openapi.component
class PlatTrie:
    code = openapi.String(
        description="Identifiant du plat",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé du plat",
        example="Dinde provençal",
    )
    ordre = openapi.Integer(
        description="Ordre du plat dans le menu",
        example=1,
    )
