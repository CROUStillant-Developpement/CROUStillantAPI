import functools

from .rules import Rules
from .response import JSON
from sanic.request import Request
from sanic.response import HTTPResponse


class Argument:
    """
    Représente un argument pour une route.

    Cette classe est utilisée pour définir et valider les arguments
    attendus dans une requête HTTP, que ce soit dans l'URL, les en-têtes,
    ou les paramètres de chemin (path parameters).
    """

    def __init__(
        self,
        name: str,
        description: str,
        methods: dict[str, Rules],
        call: callable = None,
        required: bool = True,
        headers: bool = False,
        allow_multiple: bool = False,
        deprecated: bool = False,
    ):
        """
        Initialise un nouvel argument pour une route.

        :param name: Nom de la variable attendue.
        :param description: Description du paramètre.
        :param methods: Dictionnaire des règles à appliquer {clé: règle}.
        :param call: Fonction de transformation à appliquer à la valeur (ex : int, str).
        :param required: Indique si le paramètre est requis.
        :param headers: Si True, la recherche se fait dans les en-têtes.
        :param allow_multiple: Permet plusieurs valeurs pour un même paramètre.
        :param deprecated: Marque le paramètre comme obsolète.
        """
        self.name = name
        self.description = description
        self.methods = methods
        self.call = call
        self.required = required
        self.headers = headers
        self.allow_multiple = allow_multiple
        self.deprecated = deprecated


def inputs(*args: Argument) -> callable:
    """
    Décorateur pour appliquer une validation sur les arguments d'une route.

    Ce décorateur ajoute à une fonction de route la validation des paramètres
    fournis via l'URL, les en-têtes ou les variables de chemin.

    :param args: Liste des objets Argument à valider.
    :return: La fonction décorée avec la logique de validation.
    """

    def wrapper(func) -> callable:
        """
        Décorateur interne appliquant les vérifications.

        :param func: La fonction de route à décorer.
        :return: La fonction enrichie de validation.
        """

        @functools.wraps(func)
        async def wrapped(request: Request, **kwargs) -> HTTPResponse:
            """
            Fonction exécutée à chaque appel de la route.

            :param request: L'objet représentant la requête HTTP.
            :param kwargs: Les paramètres de chemin transmis à la fonction.
            :return: Une réponse HTTP avec ou sans erreur.
            """

            def input_handler(argument: Argument) -> HTTPResponse | None:
                """
                Gère la validation d'un argument spécifique.

                :param argument: L'argument à traiter.
                :return: Une réponse HTTP d'erreur en cas d'invalidité, sinon None.
                """
                nonlocal finished_kwargs

                # Choix de la source des entrées
                if argument.headers:
                    requests_inputs = dict(request.headers)
                else:
                    requests_inputs = dict(request.args)

                    # Si non trouvé dans les query params, on regarde les path params
                    if argument.name not in requests_inputs and argument.name in kwargs:
                        requests_inputs[argument.name] = kwargs[argument.name]

                for input_name, input_rule in argument.methods.items():
                    if input_value := requests_inputs.get(input_name, None):
                        # Gestion des valeurs multiples
                        if not argument.allow_multiple and isinstance(
                            input_value, (list, tuple)
                        ):
                            if len(input_value) > 1:
                                return JSON(
                                    request=request,
                                    success=False,
                                    message=(
                                        f"Entrée invalide pour '{argument.name}'. "
                                        f"Une seule valeur attendue, plusieurs valeurs reçues."
                                    ),
                                    status=400,
                                ).generate()
                            else:
                                input_value = input_value[0]

                        # Application de la règle
                        if callable(input_rule):
                            if input_rule(input_value):
                                finished_kwargs[argument.name] = (
                                    argument.call(input_value)
                                    if argument.call
                                    else input_value
                                )
                                break
                            else:
                                return JSON(
                                    request=request,
                                    success=False,
                                    message=(
                                        f"Entrée invalide pour '{argument.name}'. "
                                        f"Attendu : '{input_rule.__name__}', reçu : '{input_value}'. "
                                        f"Info : {input_rule.__doc__.strip()}"
                                    ),
                                    status=400,
                                ).generate()
                        else:
                            finished_kwargs[argument.name] = (
                                argument.call(input_value)
                                if argument.call
                                else input_value
                            )
                            break
                else:
                    if argument.required:
                        return JSON(
                            request=request,
                            success=False,
                            message=f"Paramètre requis manquant : '{argument.name}'.",
                            status=400,
                        ).generate()
                    finished_kwargs[argument.name] = None

            finished_kwargs = kwargs.copy()

            for arg in args:
                if not isinstance(arg, Argument):
                    raise TypeError(
                        "Tous les arguments doivent être de type Argument !"
                    )

                override_exit = input_handler(argument=arg)
                if override_exit:
                    return override_exit

            return await func(request=request, **finished_kwargs)

        return wrapped

    return wrapper
