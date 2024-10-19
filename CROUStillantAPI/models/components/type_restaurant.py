from sanic_ext import openapi


@openapi.component
class TypeRestaurant:
    code = openapi.String(
        description="Identifiant du type de restauration",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé du type de restauration",
        example="Restaurant",
    )
