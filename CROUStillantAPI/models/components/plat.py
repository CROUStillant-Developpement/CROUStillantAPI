from sanic_ext import openapi


TYPES_PLAT = ["ENTREE", "PLAT", "ACCOMPAGNEMENT", "DESSERT", "FROMAGE", "BOISSON", "FORMULE", "AUTRE"]
NATURES = ["DISH", "INFO", "JUNK", "ALLERGENS", "PRICE"]


@openapi.component
class Allergene:
    code = openapi.String(
        description="Code de l'allergène (14 allergènes majeurs, règlement UE 1169/2011)",
        example="GLUTEN",
    )
    libelle = openapi.String(
        description="Libellé de l'allergène",
        example="Céréales contenant du gluten",
    )
    source = openapi.String(
        description="Origine de l'information : `CROUS` (déclaré par le restaurant dans le libellé)",
        example="CROUS",
    )
    verifie = openapi.Boolean(
        description="Information vérifiée (toujours vrai pour un allergène déclaré par le CROUS)",
        example=True,
    )


@openapi.component
class Composant:
    code = openapi.Integer(
        description="Identifiant du plat canonique (toutes écritures confondues, voir /plats/canoniques/{code})",
        example=1689,
    )
    libelle = openapi.String(
        description="Libellé du plat canonique",
        example="Poulet basquaise",
    )
    type = openapi.String(
        description="Type du plat là où il est servi (une pizza servie en « Entrées » est une entrée)",
        enum=TYPES_PLAT,
        example="PLAT",
    )
    type_defaut = openapi.String(
        description="Type par défaut du plat canonique",
        enum=TYPES_PLAT,
        example="PLAT",
    )
    vegetarien = openapi.Boolean(
        description="Plat annoncé végétarien",
        example=False,
    )


@openapi.component
class Analyse:
    nature = openapi.String(
        description="DISH (plat), INFO (fermeture, horaire, information...), JUNK (séparateur...), "
        "ALLERGENS ou PRICE (ligne isolée)",
        enum=NATURES,
        example="DISH",
    )
    type_info = openapi.String(
        description="Type d'information si nature = INFO : CLOSURE, NOTICE, APP, THEME, CATEGORY, HUMAIN",
        example=None,
        nullable=True,
    )
    libelle = openapi.String(
        description="Libellé nettoyé (sans points, prix, codes allergènes...)",
        example="Poulet basquaise",
        nullable=True,
    )
    type = openapi.String(
        description="Type du composant principal là où il est servi",
        enum=TYPES_PLAT,
        example="PLAT",
        nullable=True,
    )
    points = openapi.Float(
        description="Coût en points (restaurants à points)",
        example=4.0,
        nullable=True,
    )
    prix = openapi.Array(
        items=openapi.Float(),
        description="Prix indiqués dans le libellé (€)",
        example=[],
    )
    allergenes_declares = openapi.Array(
        items=Allergene,
        description="Allergènes déclarés dans le libellé par le restaurant (ex : « (1.3.7) »)",
    )
    vegetarien = openapi.Boolean(
        description="Plat annoncé végétarien",
        example=False,
    )
    origines = openapi.Array(
        items=openapi.String(),
        description="Origines annoncées",
        example=["France"],
    )
    labels = openapi.Array(
        items=openapi.String(),
        description="Labels annoncés (bio, maison, label rouge...)",
        example=["maison"],
    )
    composants = openapi.Array(
        items=Composant,
        description="Plats canoniques contenus dans le libellé (« Poisson pané, riz, ratatouille » → 3 composants)",
    )


@openapi.component
class Plat:
    code = openapi.String(
        description="Identifiant du plat",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé du plat",
        example="Dinde provençal",
    )
    # analyse du libellé (null si le plat n'a pas encore été analysé)
    analyse = Analyse


@openapi.component
class PlatTrie:
    code = openapi.String(
        description="Identifiant du plat",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé du plat",
        example="Dinde provençal",
    )
    ordre = openapi.Integer(
        description="Ordre du plat dans le menu",
        example=1,
    )
    # analyse du libellé (null si le plat n'a pas encore été analysé)
    analyse = Analyse


class PlatWithTotal:
    code = openapi.String(
        description="Identifiant du plat",
        example=1,
    )
    libelle = openapi.String(
        description="Libellé du plat",
        example="Dinde provençal",
    )
    total = openapi.Integer(
        description="Nombre de fois d'apparition du plat",
        example=10,
    )


@openapi.component
class PlatCanonique:
    code = openapi.Integer(
        description="Identifiant du plat canonique",
        example=1689,
    )
    libelle = openapi.String(
        description="Libellé du plat canonique",
        example="Poulet basquaise",
    )
    type = openapi.String(
        description="Type par défaut",
        enum=TYPES_PLAT,
        example="PLAT",
    )
    vegetarien = openapi.Boolean(
        description="Plat annoncé végétarien",
        example=False,
    )
    verifie = openapi.Boolean(
        description="Type vérifié à la main",
        example=False,
    )
    nb_libelles = openapi.Integer(
        description="Nombre de libellés bruts qui désignent ce plat",
        example=42,
    )
    libelles = openapi.Array(
        items=Plat,
        description="Quelques libellés bruts qui désignent ce plat (les plus récents)",
    )


@openapi.component
class AnalyseRequete:
    libelle = openapi.String(
        description="Libellé brut à analyser (500 caractères maximum)",
        example="Sauté de porc aux pruneaux - 5 pts (1.3.7)",
    )
    categorie = openapi.String(
        description="Catégorie du menu où le plat est servi (optionnel, affine le type)",
        example="Plats",
    )


@openapi.component
class ComposantAnalyse:
    libelle = openapi.String(
        description="Libellé du composant",
        example="Sauté de porc aux pruneaux",
    )
    type = openapi.String(
        description="Type du composant (là où il est servi si une catégorie est fournie)",
        enum=TYPES_PLAT,
        example="PLAT",
    )
    type_defaut = openapi.String(
        description="Type par défaut (base de données si le plat est connu, sinon règles)",
        enum=TYPES_PLAT,
        example="PLAT",
    )
    confiance = openapi.Float(
        description="Confiance dans le type par défaut (0 à 1)",
        example=0.95,
    )
    source = openapi.String(
        description="Origine du type : `base` (plat connu), `humain` (vérifié à la main) ou règle du classifieur",
        example="base",
    )
    connu = openapi.Boolean(
        description="Le plat existe déjà dans la base (plat canonique)",
        example=True,
    )
    code = openapi.Integer(
        description="Identifiant du plat canonique s'il est connu",
        example=1689,
        nullable=True,
    )
    vegetarien = openapi.Boolean(
        description="Plat annoncé végétarien",
        example=False,
    )
    a_verifier = openapi.Boolean(
        description="Le type est incertain",
        example=False,
    )


@openapi.component
class AnalyseResultat:
    libelle = openapi.String(description="Libellé brut reçu", example="Sauté de porc aux pruneaux - 5 pts (1.3.7)")
    nature = openapi.String(description="Nature du libellé", enum=NATURES, example="DISH")
    type_info = openapi.String(description="Type d'information si nature = INFO", example=None, nullable=True)
    libelle_net = openapi.String(description="Libellé nettoyé", example="Sauté de porc aux pruneaux", nullable=True)
    type = openapi.String(description="Type du composant principal", enum=TYPES_PLAT, example="PLAT", nullable=True)
    points = openapi.Float(description="Coût en points", example=5.0, nullable=True)
    prix = openapi.Array(items=openapi.Float(), description="Prix indiqués (€)", example=[])
    allergenes_declares = openapi.Array(items=Allergene, description="Allergènes déclarés dans le libellé")
    vegetarien = openapi.Boolean(description="Plat annoncé végétarien", example=False)
    origines = openapi.Array(items=openapi.String(), description="Origines annoncées", example=[])
    labels = openapi.Array(items=openapi.String(), description="Labels annoncés", example=[])
    composants = openapi.Array(items=ComposantAnalyse, description="Plats contenus dans le libellé")
    version = openapi.String(description="Version du classifieur", example="2.0.0")
