from sanic.exceptions import SanicException


class ForbiddenException(SanicException):
    status_code = 403
    quiet = True

    @property
    def message(self):
        if self.extra["ban"]:
            return "Vous avez été banni du service pour non-respect des règles d'utilisation. Si vous pensez qu'il s'agit d'une erreur, veuillez nous contacter à l'adresse suivante : croustillant@bayfield.dev."
        else:
            return "Vous n'avez pas les permissions nécessaires pour accéder à cette ressource. Si vous pensez qu'il s'agit d'une erreur, veuillez nous contacter à l'adresse suivante : croustillant@bayfield.dev."
