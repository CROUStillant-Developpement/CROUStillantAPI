from sanic_ext import openapi


@openapi.component
class Region:
    code = openapi.String(
        description="Identifiant de la région",
        example=23,
    )
    libelle = openapi.String(
        description="Libellé de la région",
        example="Reims",
    )
