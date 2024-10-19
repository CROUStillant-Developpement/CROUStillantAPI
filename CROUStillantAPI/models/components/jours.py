from sanic_ext import openapi


class Ouverture:
    matin = openapi.Boolean(
        description="Ouverture le matin",
        example=True,
    )
    midi = openapi.Boolean(
        description="Ouverture le midi",
        example=True,
    )
    soir = openapi.Boolean(
        description="Ouverture le soir",
        example=True,
    )


@openapi.component
class Jours:
    jour = openapi.String(
        description="Jours de la semaine",
        example="Lundi",
    )
    ouverture = Ouverture
