import re
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

    @staticmethod
    def iframe_theme(arg: str) -> bool:
        """
        Le thème doit être 'light' ou 'dark'.
        """
        return arg.lower() in ("light", "dark")

    @staticmethod
    def iframe_lang(arg: str) -> bool:
        """
        La langue doit être 'fr' ou 'en'.
        """
        return arg.lower() in ("fr", "en")

    @staticmethod
    def iframe_font(arg: str) -> bool:
        """
        La police doit être l'une des valeurs suivantes : Inter, Roboto, Outfit, Nunito, system.
        """
        return arg in ("Inter", "Roboto", "Outfit", "Nunito", "system")

    @staticmethod
    def iframe_height(arg: str | int) -> bool:
        """
        La hauteur doit être un entier compris entre 200 et 1200 (en pixels).
        """
        try:
            return 200 <= int(arg) <= 1200
        except (ValueError, TypeError):
            return False

    @staticmethod
    def iframe_blocks(arg: str) -> bool:
        """
        Les blocs doivent être une liste d'identifiants séparés par des virgules.
        Valeurs autorisées : header, header_text, region, status, address, menu, hours, contact, payment, access, link.
        Au moins un bloc doit être présent, sans doublon.
        """
        _allowed = frozenset((
            "header", "header_text", "region", "status", "address",
            "menu", "hours", "contact", "payment", "access", "link",
        ))
        parts = [b.strip() for b in arg.split(",") if b.strip()]
        return len(parts) > 0 and len(parts) == len(set(parts)) and all(b in _allowed for b in parts)

    @staticmethod
    def iframe_meals(arg: str) -> bool:
        """
        Les repas doivent être une liste séparée par des virgules.
        Valeurs autorisées : matin, midi, soir.
        Au moins un repas doit être présent, sans doublon.
        """
        _allowed = frozenset(("matin", "midi", "soir"))
        parts = [m.strip() for m in arg.split(",") if m.strip()]
        return len(parts) > 0 and len(parts) == len(set(parts)) and all(m in _allowed for m in parts)

    @staticmethod
    def hex_color(arg: str) -> bool:
        """
        Une couleur hexadécimale sans le symbole # composée de 6 caractères parmi 0-9 et a-f (insensible à la casse).
        """
        return bool(re.fullmatch(r"[0-9a-fA-F]{6}", arg))
