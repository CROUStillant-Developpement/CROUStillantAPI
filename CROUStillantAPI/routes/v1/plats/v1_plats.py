from ....components.ratelimit import ratelimit
from ....components.cache import cache
from ....components.response import JSON
from ....components.argument import Argument, inputs
from ....components.rules import Rules
from ....models.responses import Plats, Plat, PlatsWithTotal, PlatCanonique, AnalysePlat
from ....models.components import AnalyseRequeteComponent
from ....utils.plat import format_analyse, format_allergenes
from croustillant_classifier import VERSION, occurrence_type
from ....models.exceptions import RateLimited, BadRequest, NotFound
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(name="Plats", url_prefix="/plats", version=1, version_prefix="v")


# /plats
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="Liste des 100 derniers plats",
    description="Liste des 100 derniers plats ajoutés à la base de données.",
    tag="Plats",
)
@openapi.response(
    status=200,
    content={"application/json": Plats},
    description="Liste des 100 derniers plats ajoutés à la base de données.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
@cache(ttl=300)
async def getPlats(request: Request) -> JSONResponse:
    """
    Récupère les 100 derniers plats ajoutés à la base de données

    :return: Les plats
    """
    # plats = await request.app.ctx.entities.plats.getAll()
    plats = await request.app.ctx.entities.plats.getLast(100)

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": plat.get("platid"),
                "libelle": plat.get("libelle"),
                "analyse": format_analyse(plat),
            }
            for plat in plats
        ],
        status=200,
    ).generate()


# /plats/{code}
@bp.route("/<code>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un plat",
    description="Détails d'un plat en fonction de son code.",
    tag="Plats",
)
@openapi.response(
    status=200, content={"application/json": Plat}, description="Détails d'un plat."
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du plat doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le plat n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du plat",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@ratelimit()
@inputs(
    Argument(
        name="code",
        description="ID du plat",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@cache(ttl=300)
async def getPlat(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'un plat.

    :param code: ID du plat
    :return: Le plat
    """
    plat = await request.app.ctx.entities.plats.getOne(code)

    if plat is None:
        return JSON(
            request=request, success=False, status=404, message="Le plat n'existe pas."
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "code": plat.get("platid"),
            "libelle": plat.get("libelle"),
            "analyse": format_analyse(plat),
        },
        status=200,
    ).generate()


# /plats/top
@bp.route("/top", methods=["GET"])
@openapi.definition(
    summary="Top 100 des plats",
    description="Top 100 des plats les plus populaires.",
    tag="Plats",
)
@openapi.response(
    status=200,
    content={"application/json": PlatsWithTotal},
    description="Top 100 des plats les plus populaires.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
@cache(ttl=300)
async def getPlatTop(request: Request) -> JSONResponse:
    """
    Retourne le top 100 des plats.

    :return: Le top 100 des plats
    """
    plats = await request.app.ctx.entities.plats.getTop(100)

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "code": plat.get("platid"),
                "libelle": plat.get("libelle"),
                "total": plat.get("nb"),
            }
            for plat in plats
        ],
        status=200,
    ).generate()


# /plats/canoniques/{code}
@bp.route("/canoniques/<code>", methods=["GET"])
@openapi.definition(
    summary="Détails d'un plat canonique",
    description="Un plat canonique regroupe toutes les écritures d'un même plat "
    "(« Poulet à la basquaise », « POULET BASQUAISE (maison) »...). Son code est donné par "
    "`analyse.composants[].code` dans les menus et les plats.",
    tag="Plats",
)
@openapi.response(
    status=200,
    content={"application/json": PlatCanonique},
    description="Détails d'un plat canonique.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="L'ID du plat canonique doit être un nombre.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="Le plat canonique n'existe pas.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@openapi.parameter(
    name="code",
    description="ID du plat canonique",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@ratelimit()
@inputs(
    Argument(
        name="code",
        description="ID du plat canonique",
        methods={"code": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    )
)
@cache(ttl=300)
async def getPlatCanonique(request: Request, code: int) -> JSONResponse:
    """
    Retourne les détails d'un plat canonique.

    :param code: ID du plat canonique
    :return: Le plat canonique
    """
    canonique, libelles = await request.app.ctx.entities.plats.getCanonique(code)

    if canonique is None:
        return JSON(
            request=request,
            success=False,
            status=404,
            message="Le plat canonique n'existe pas.",
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "code": canonique.get("idpc"),
            "libelle": canonique.get("libelle"),
            "type": canonique.get("type_plat"),
            "vegetarien": canonique.get("vegetarien"),
            "verifie": canonique.get("source") == "humain",
            "nb_libelles": canonique.get("nb_libelles"),
            "libelles": [
                {"code": row.get("platid"), "libelle": row.get("libelle")}
                for row in libelles
            ],
        },
        status=200,
    ).generate()


# /plats/analyse
@bp.route("/analyse", methods=["POST"])
@openapi.definition(
    summary="Analyser un libellé",
    description="Analyse un libellé de plat tel qu'écrit par un restaurant : nature (plat ou "
    "information), libellé nettoyé, points, prix, allergènes déclarés, régime, et type de chaque "
    "plat qu'il contient. Un plat déjà connu prend le type enregistré dans la base (éventuellement "
    "vérifié à la main), un plat inconnu celui des règles du classifieur.",
    tag="Plats",
)
@openapi.body(
    {"application/json": AnalyseRequeteComponent},
    description="Le libellé à analyser et, si connue, la catégorie du menu.",
    required=True,
)
@openapi.response(
    status=200,
    content={"application/json": AnalysePlat},
    description="Analyse du libellé.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="Le corps de la requête est invalide.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="Vous avez envoyé trop de requêtes. Veuillez réessayer plus tard.",
)
@ratelimit()
async def postPlatAnalyse(request: Request) -> JSONResponse:
    """
    Analyse un libellé de plat.

    :return: L'analyse du libellé
    """
    try:
        body = request.json
    except Exception:
        body = None

    if not isinstance(body, dict):
        return JSON(
            request=request,
            success=False,
            status=400,
            message="Le corps de la requête doit être un objet JSON : {\"libelle\": \"...\", \"categorie\": \"...\"}.",
        ).generate()

    libelle = body.get("libelle")
    categorie = body.get("categorie")

    if not isinstance(libelle, str) or not libelle.strip() or len(libelle) > 500:
        return JSON(
            request=request,
            success=False,
            status=400,
            message="Le champ `libelle` est obligatoire (texte de 1 à 500 caractères).",
        ).generate()

    if categorie is not None and (not isinstance(categorie, str) or len(categorie) > 500):
        return JSON(
            request=request,
            success=False,
            status=400,
            message="Le champ `categorie` doit être un texte de 500 caractères maximum.",
        ).generate()

    categorie = categorie.strip() or None if categorie else None
    analyse = request.app.ctx.classifier.analyse(libelle, categorie)
    parsed = analyse.parsed

    # un plat déjà connu prend le type de la base (éventuellement vérifié à la main)
    connus = await request.app.ctx.entities.plats.getCanoniquesByKeys(
        [c.key for c in analyse.components]
    )

    composants = []
    for i, c in enumerate(analyse.components):
        connu = connus.get(c.key)
        type_defaut = connu.get("type_plat") if connu else c.type
        humain = connu is not None and connu.get("source") == "humain"

        composants.append(
            {
                "libelle": connu.get("libelle") if connu else c.label,
                "type": occurrence_type(type_defaut, categorie, main_component=i == 0),
                "type_defaut": type_defaut,
                "confiance": 1.0 if humain else round(connu.get("confiance") if connu else c.confidence, 2),
                "source": "humain" if humain else ("base" if connu else c.source),
                "connu": connu is not None,
                "code": connu.get("idpc") if connu else None,
                "vegetarien": c.vegetarian,
                "a_verifier": connu.get("a_revoir") if connu else c.needs_review,
            }
        )

    return JSON(
        request=request,
        success=True,
        data={
            "libelle": libelle,
            "nature": parsed.kind if analyse.is_dish or parsed.kind != "DISH" else "INFO",
            "type_info": parsed.info_kind,
            "libelle_net": parsed.name or None,
            "type": composants[0]["type"] if composants else None,
            "points": parsed.points,
            "prix": parsed.prices,
            "allergenes_declares": format_allergenes(parsed.allergen_ids),
            "vegetarien": analyse.vegetarian if analyse.components else parsed.vegetarian,
            "origines": parsed.origins,
            "labels": parsed.labels,
            "composants": composants,
            "version": VERSION,
        },
        status=200,
    ).generate()
