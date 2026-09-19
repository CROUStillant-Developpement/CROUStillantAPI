from sanic_ext import openapi


class ApiRoute:
    route = openapi.String(
        description="Route de l'API (les segments variables sont remplacés par <code>, <date>, ...)",
        example="/v1/restaurants/<code>/menu",
    )
    requetes = openapi.Integer(
        description="Nombre total de requêtes sur cette route",
        example=1250000,
    )
    temps_moyen_ms = openapi.Float(
        description="Temps de traitement moyen en millisecondes",
        example=18.4,
    )


class ApiStatsData:
    requetes = openapi.Integer(
        description="Nombre total de requêtes reçues depuis le début du suivi",
        example=8500000,
    )
    visiteurs_uniques = openapi.Integer(
        description="Nombre d'adresses IP distinctes (anonymisées) depuis le début du suivi",
        example=42000,
    )
    depuis = openapi.String(
        description="Premier jour du suivi",
        example="01-09-2025",
    )
    routes = openapi.Array(
        items=ApiRoute,
        description="Les 10 routes publiques les plus appelées",
    )


class ApiStats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = ApiStatsData


class ApiStatsDay:
    jour = openapi.String(
        description="Jour",
        example="18-09-2026",
    )
    requetes = openapi.Integer(
        description="Nombre de requêtes reçues",
        example=32000,
    )
    visiteurs_uniques = openapi.Integer(
        description="Nombre d'adresses IP distinctes (anonymisées)",
        example=850,
    )
    erreurs_serveur = openapi.Integer(
        description="Nombre de réponses en erreur serveur (5xx)",
        example=3,
    )
    temps_reponse_p50_ms = openapi.Float(
        description="Temps de traitement médian en millisecondes",
        example=12.0,
    )
    temps_reponse_p95_ms = openapi.Float(
        description="95e centile du temps de traitement en millisecondes",
        example=85.5,
    )


class ApiStatsHistory:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=ApiStatsDay,
        description="Évolution journalière (jours terminés uniquement), du plus ancien au plus récent",
    )
