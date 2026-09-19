from sanic_ext import openapi


class BotStatsData:
    statut = openapi.String(
        description="Statut du bot lors du dernier relevé : online, degraded (certains shards hors ligne), starting ou offline",
        example="online",
    )
    date = openapi.String(
        description="Date du dernier relevé (UTC, relevé toutes les 5 minutes)",
        example="18-09-2026 14:35:00",
    )
    latence_ms = openapi.Float(
        description="Latence du bot avec Discord en millisecondes (null si hors ligne)",
        example=42.5,
    )
    serveurs = openapi.Integer(
        description="Nombre de serveurs Discord (dernier relevé où le bot était joignable)",
        example=120,
    )
    utilisateurs = openapi.Integer(
        description="Nombre total de membres des serveurs",
        example=45210,
    )
    salons = openapi.Integer(
        description="Nombre de salons des serveurs",
        example=2400,
    )
    shards = openapi.Integer(
        description="Nombre de shards",
        example=1,
    )
    disponibilite_24h = openapi.Float(
        description="Pourcentage de relevés où le bot était en ligne sur les dernières 24 heures",
        example=100.0,
    )
    disponibilite_30j = openapi.Float(
        description="Pourcentage de relevés où le bot était en ligne sur les 30 derniers jours",
        example=99.86,
    )


class BotStats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = BotStatsData


class BotStatsDay:
    jour = openapi.String(
        description="Jour (Europe/Paris)",
        example="18-09-2026",
    )
    serveurs = openapi.Integer(
        description="Nombre de serveurs Discord en fin de journée",
        example=120,
    )
    utilisateurs = openapi.Integer(
        description="Nombre total de membres des serveurs en fin de journée",
        example=45210,
    )
    salons = openapi.Integer(
        description="Nombre de salons des serveurs en fin de journée",
        example=2400,
    )
    shards = openapi.Integer(
        description="Nombre de shards en fin de journée",
        example=1,
    )
    latence_ms = openapi.Float(
        description="Latence moyenne du bot avec Discord sur la journée, en millisecondes",
        example=41.87,
    )
    disponibilite = openapi.Float(
        description="Pourcentage de relevés de la journée où le bot était en ligne",
        example=100.0,
    )
    releves = openapi.Integer(
        description="Nombre de relevés de la journée (288 pour une journée complète)",
        example=288,
    )


class BotStatsHistory:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=BotStatsDay,
        description="Évolution journalière, du plus ancien au plus récent",
    )
