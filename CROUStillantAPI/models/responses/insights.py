from sanic_ext import openapi


class Periode:
    debut = openapi.String(
        description="Début de la période (DD-MM-YYYY)",
        example="01-09-2025",
    )
    fin = openapi.String(
        description="Fin de la période (DD-MM-YYYY)",
        example="11-07-2026",
    )


class Couverture:
    jours_ouvres = openapi.Integer(
        description="Nombre de jours d'ouverture attendus sur la période",
        example=180,
    )
    jours_avec_menu = openapi.Integer(
        description="Nombre de jours avec un menu publié",
        example=162,
    )
    jours_sans_menu = openapi.Integer(
        description="Nombre de jours sans menu publié",
        example=18,
    )
    taux_couverture = openapi.Float(
        description="Taux de couverture en pourcentage",
        example=90.0,
    )


class RepartitionRepas:
    matin = openapi.Integer(
        description="Nombre de petits-déjeuners servis sur la période",
        example=0,
    )
    midi = openapi.Integer(
        description="Nombre de déjeuners servis sur la période",
        example=178,
    )
    soir = openapi.Integer(
        description="Nombre de dîners servis sur la période",
        example=34,
    )


class PlatFrequent:
    code = openapi.Integer(
        description="Identifiant du plat (PLATID)",
        example=1234,
    )
    libelle = openapi.String(
        description="Libellé du plat",
        example="Poulet rôti",
    )
    total = openapi.Integer(
        description="Nombre d'occurrences du plat sur la période",
        example=14,
    )


class CouvertureJour:
    jour = openapi.String(
        description="Jour de la semaine",
        example="Lundi",
    )
    jours_ouvres = openapi.Integer(
        description="Nombre d'occurrences de ce jour sur la période où le restaurant est censé être ouvert",
        example=26,
    )
    jours_avec_menu = openapi.Integer(
        description="Nombre d'occurrences de ce jour avec un menu publié",
        example=24,
    )
    taux_couverture = openapi.Float(
        description="Taux de couverture pour ce jour en pourcentage",
        example=92.3,
    )


class SerieActuelle:
    avec_menu = openapi.Boolean(
        description="La série en cours est-elle une série de jours avec menu (true) ou sans menu (false) ?",
        example=True,
    )
    jours = openapi.Integer(
        description="Longueur de la série en cours (en jours d'ouverture)",
        example=12,
    )


class Series:
    meilleure_serie_avec_menu = openapi.Integer(
        description="Plus longue série de jours d'ouverture consécutifs avec un menu publié",
        example=45,
    )
    plus_longue_serie_sans_menu = openapi.Integer(
        description="Plus longue série de jours d'ouverture consécutifs sans menu publié",
        example=3,
    )
    serie_actuelle = SerieActuelle


class Variete:
    plats_uniques = openapi.Integer(
        description="Nombre de plats distincts servis sur la période",
        example=214,
    )
    plats_total = openapi.Integer(
        description="Nombre total de plats servis sur la période (occurrences)",
        example=480,
    )
    taux_variete = openapi.Float(
        description="Taux de variété (plats_uniques / plats_total) en pourcentage",
        example=44.6,
    )


class Richesse:
    moyenne_categories_par_repas = openapi.Float(
        description="Nombre moyen de catégories par repas",
        example=3.2,
    )
    moyenne_plats_par_repas = openapi.Float(
        description="Nombre moyen de plats par repas",
        example=5.8,
    )


class DelaiPublication:
    moyenne_jours = openapi.Float(
        description="Délai moyen (en jours) entre l'ingestion d'un menu et sa date d'application (positif = publié à l'avance)",
        example=2.4,
        nullable=True,
    )


class ComparaisonRegionale:
    jours_avec_menu_restaurant = openapi.Integer(
        description="Nombre de jours avec menu pour ce restaurant sur la période",
        example=162,
    )
    moyenne_jours_avec_menu_region = openapi.Float(
        description="Moyenne du nombre de jours avec menu pour les autres restaurants actifs de la région",
        example=148.5,
        nullable=True,
    )
    nb_restaurants_compares = openapi.Integer(
        description="Nombre de restaurants de la région utilisés pour la comparaison",
        example=12,
    )


class Data:
    periode = Periode
    couverture = Couverture
    repartition_repas = RepartitionRepas
    plats_frequents = openapi.Array(
        items=PlatFrequent,
        description="Liste des plats les plus fréquents sur la période",
    )
    couverture_par_jour = openapi.Array(
        items=CouvertureJour,
        description="Répartition de la couverture des menus par jour de la semaine",
    )
    series = Series
    variete = Variete
    richesse = Richesse
    delai_publication = DelaiPublication
    comparaison_regionale = ComparaisonRegionale


class RestaurantInsights:
    success = openapi.Boolean(
        description="Statut de la requête",
        example=True,
    )
    data = Data
