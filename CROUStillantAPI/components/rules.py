from datetime import datetime


class Rules:
    @staticmethod
    def boolean(arg: str) -> bool:
        """
        Un booléen est une chaîne de caractères qui peut être soit "true" soit "false".
        """
        return arg.lower() in ["true", "false"]

    @staticmethod
    def integer(arg: str | int) -> bool:
        """
        Un entier est une chaîne de caractères qui ne peut contenir que des chiffres. Il doit être positif.
        """
        try:
            return str(arg).isdigit()
        except Exception:
            return False

    @staticmethod
    def float(arg: str | int) -> bool:
        """
        Un flottant est une chaîne de caractères qui peut contenir uniquement des chiffres et un point décimal. Il doit être positif.
        """
        try:
            return float(arg) >= 0
        except ValueError:
            return False

    @staticmethod
    def timestamp_ms(arg: str | int) -> bool:
        """
        Un timestamp en millisecondes est une chaîne de caractères qui ne peut contenir que des chiffres. Il doit comporter 13 caractères.
        """
        return all([x in "0123456789" for x in str(arg)]) and len(str(arg)) == 13

    @staticmethod
    def timestamp_s(arg: str | int) -> bool:
        """
        Un timestamp en secondes est une chaîne de caractères qui ne peut contenir que des chiffres. Il doit comporter 10 caractères.
        """
        return all([x in "0123456789" for x in str(arg)]) and len(str(arg)) == 10

    @staticmethod
    def timestamp(arg: str) -> bool:
        """
        Un timestamp peut être au format millisecondes (13 caractères) ou secondes (10 caractères).
        """
        return Rules.timestamp_ms(arg) or Rules.timestamp_s(arg)

    @staticmethod
    def history(arg: str | int) -> bool:
        """
        Un historique est une chaîne de caractères qui ne peut contenir que des chiffres. Il doit être compris entre 1 et 365 caractères.
        """
        return Rules.integer(arg) and 1 <= int(arg) <= 365

    @staticmethod
    def date(arg: str) -> bool:
        """
        Une date est une chaîne de caractères au format DD-MM-YYYY.
        """
        try:
            datetime.strptime(arg, "%d-%m-%Y")
            return True
        except ValueError:
            return False
