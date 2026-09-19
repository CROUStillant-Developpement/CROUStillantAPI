from sanic_ext import openapi
from ..components import TacheComponent, TacheWithRestaurantsComponent


class Taches:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(description="Liste des tâches", items=TacheComponent)


class Tache:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = TacheWithRestaurantsComponent


class TacheStatsDerniere:
    id = openapi.Integer(
        description="ID de la tâche",
        example=12345,
    )
    debut = openapi.String(
        description="Date de début (UTC)",
        example="18-09-2026 13:00:00",
    )
    fin = openapi.String(
        description="Date de fin (UTC), null si la tâche est en cours ou a échoué",
        example="18-09-2026 13:04:12",
    )


class TacheStatsTerminee:
    id = openapi.Integer(
        description="ID de la tâche",
        example=12345,
    )
    debut = openapi.String(
        description="Date de début (UTC)",
        example="18-09-2026 13:00:00",
    )
    fin = openapi.String(
        description="Date de fin (UTC) : dernière mise à jour des données",
        example="18-09-2026 13:04:12",
    )
    duree = openapi.Float(
        description="Durée de la tâche en secondes",
        example=252.4,
    )
    requetes = openapi.Integer(
        description="Nombre de requêtes envoyées aux services du CROUS",
        example=1900,
    )
    nouveaux_menus = openapi.Integer(
        description="Nombre de menus ajoutés",
        example=120,
    )
    nouveaux_repas = openapi.Integer(
        description="Nombre de repas ajoutés",
        example=180,
    )
    nouveaux_plats = openapi.Integer(
        description="Nombre de nouveaux plats (jamais vus auparavant)",
        example=14,
    )


class TachesStatsData:
    derniere = TacheStatsDerniere
    derniere_terminee = TacheStatsTerminee
    taches_24h = openapi.Integer(
        description="Nombre de tâches terminées sur les dernières 24 heures",
        example=9,
    )
    duree_moyenne_7j = openapi.Float(
        description="Durée moyenne des tâches terminées sur les 7 derniers jours, en secondes",
        example=240.8,
    )


class TachesStats:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = TachesStatsData


class TachesStatsDay:
    jour = openapi.String(
        description="Jour",
        example="18-09-2026",
    )
    taches = openapi.Integer(
        description="Nombre de tâches terminées",
        example=9,
    )
    duree_moyenne = openapi.Float(
        description="Durée moyenne des tâches en secondes",
        example=240.8,
    )
    requetes = openapi.Integer(
        description="Nombre de requêtes envoyées aux services du CROUS",
        example=17000,
    )
    nouveaux_menus = openapi.Integer(
        description="Nombre de menus ajoutés",
        example=950,
    )
    nouveaux_repas = openapi.Integer(
        description="Nombre de repas ajoutés",
        example=1400,
    )
    nouveaux_plats = openapi.Integer(
        description="Nombre de nouveaux plats",
        example=60,
    )


class TachesStatsHistory:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = openapi.Array(
        items=TachesStatsDay,
        description="Évolution journalière, du plus ancien au plus récent",
    )
