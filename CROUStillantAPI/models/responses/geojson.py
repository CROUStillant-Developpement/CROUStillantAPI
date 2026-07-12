from sanic_ext import openapi


class GeoJSON:
    type = openapi.String(
        description="Type GeoJSON",
        example="FeatureCollection",
    )
    features = openapi.Array(
        items=openapi.Object(),
        description="Une feature par CROUS (propriétés crous_id, crous_slug, crous_libelle, crous_nom, departements + géométrie du territoire)",
    )
