from sanic_ext import openapi


class Unauthorized:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=False,
    )
    message = openapi.String(
        description="Message de retour",
        example="La ressource demandée nécessite une authentification valide.",
    )
