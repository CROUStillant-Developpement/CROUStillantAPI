from sanic_ext import openapi


class ActivityRun:
    id = openapi.Integer(
        description="Identifiant de la tâche d'ingestion",
        example=12345,
    )
    debut = openapi.String(
        description="Date et heure de début de la tâche (DD-MM-YYYY HH:MM:SS)",
        example="11-07-2026 06:00:00",
    )
    fin = openapi.String(
        description="Date et heure de fin de la tâche (DD-MM-YYYY HH:MM:SS)",
        example="11-07-2026 06:04:12",
        nullable=True,
    )


class Data:
    ajout = openapi.String(
        description="Date d'ajout du restaurant dans la base de données (DD-MM-YYYY HH:MM:SS)",
        example="13-11-2023 12:00:00",
    )
    modifie = openapi.String(
        description="Date de dernière mise à jour du restaurant (DD-MM-YYYY HH:MM:SS)",
        example="11-07-2026 06:04:12",
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
