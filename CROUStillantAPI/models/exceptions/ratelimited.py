from sanic_ext import openapi


class RateLimited:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=False,
    )
    message = openapi.String(
        description="Message de retour",
        example="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard."
    )
