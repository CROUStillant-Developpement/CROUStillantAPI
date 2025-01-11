from sanic_ext import openapi


class ChangeLogObject:
    date = openapi.String(
        description="Date de la version",
        example="2024-12-30T11:57:00Z",
    )
    version = openapi.String(
        description="Version de l'API",
        example="v1.0.0",
    )
    fr = openapi.Object(
        description="Informations en français",
        properties={
            "title": openapi.String(
                description="Titre de la version",
                example="CROUStillant Web",
            ),
            "shortDescription": openapi.String(
                description="Description courte de la version",
                example="CROUStillant Web est une version web de CROUStillant, accessible depuis n'importe quel navigateur.",
            ),
            "fullDescription": openapi.String(
                description="Description complète de la version",
                example="CROUStillant Web est une version web de CROUStillant, accessible depuis n'importe quel navigateur. Cette version permet de consulter les menus de la semaine, de la journée, et de la soirée des Restaurants Universitaires de France et d'outre-mer.",
            ),
        },
    )
    en = openapi.Object(
        description="Informations en anglais",
        properties={
            "title": openapi.String(
                description="Titre de la version",
                example="CROUStillant Web",
            ),
            "shortDescription": openapi.String(
                description="Description courte de la version",
                example="CROUStillant Web is a web version of CROUStillant, accessible from any browser.",
            ),
            "fullDescription": openapi.String(
                description="Description complète de la version",
                example="CROUStillant Web is a web version of CROUStillant, accessible from any browser. This version allows you to view the menus for the week, the day, and the evening of University Restaurants in France and overseas.",
            ),
        },
    )
    contributors = openapi.Array(
        description="Liste des contributeurs",
        items=openapi.Object(
            properties={
                "name": openapi.String(
                    description="Nom du contributeur",
                    example="Paul Bayfield",
                ),
                "role": openapi.Object(
                    description="Rôle du contributeur",
                    properties={
                        "fr": openapi.String(
                            description="Rôle du contributeur en français",
                            example="Fondateur du projet et développeur principal",
                        ),
                        "en": openapi.String(
                            description="Rôle du contributeur en anglais",
                            example="Project founder and lead developer",
                        ),
                    },
                ),
            },
        ),
    )


@openapi.component
class ChangeLog:
    CROUStillant = openapi.Array(
        description="Changelog des services de CROUStillant",
        items=ChangeLogObject,
    )
