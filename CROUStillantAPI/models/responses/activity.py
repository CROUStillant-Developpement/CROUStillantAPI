from sanic_ext import openapi


class ActivityRun:
    id = openapi.Integer(
        description="Identifiant de la tâche d'ingestion",
        example=12345,
    )
    debut = openapi.String(
        description="Date et heure de début de la tâche (YYYY-MM-DD HH:MM:SS)",
        example="2026-07-11 06:00:00",
    )
    fin = openapi.String(
        description="Date et heure de fin de la tâche (YYYY-MM-DD HH:MM:SS)",
        example="2026-07-11 06:04:12",
        nullable=True,
    )


class Data:
    ajout = openapi.String(
        description="Date d'ajout du restaurant dans la base de données",
        example="2023-11-13 12:00:00",
    )
    modifie = openapi.String(
        description="Date de dernière mise à jour du restaurant",
        example="2026-07-11 06:04:12",
        nullable=True,
    )
    nb_verifications = openapi.Integer(
        description="Nombre total de tâches d'ingestion ayant vérifié ce restaurant",
        example=842,
    )
    dernieres_verifications = openapi.Array(
        items=ActivityRun,
        description="Les dernières tâches d'ingestion ayant vérifié ce restaurant, les plus récentes en premier",
    )


class RestaurantActivity:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = Data
