from enum import Enum


class Weights(Enum):
    """
    Poids du texte pour la police Inter.

    :cvar THIN: Poids fin
    :cvar THIN_ITALIC: Poids fin italique
    :cvar EXTRA_LIGHT: Poids extra léger
    :cvar EXTRA_LIGHT_ITALIC: Poids extra léger italique
    :cvar LIGHT: Poids léger
    :cvar LIGHT_ITALIC: Poids léger italique
    :cvar REGULAR: Poids normal
    :cvar ITALIC: Poids normal italique
    :cvar MEDIUM: Poids moyen
    :cvar MEDIUM_ITALIC: Poids moyen italique
    :cvar SEMI_BOLD: Poids semi-gras
    :cvar SEMI_BOLD_ITALIC: Poids semi-gras italique
    :cvar BOLD: Poids gras
    :cvar BOLD_ITALIC: Poids gras italique
    :cvar EXTRA_BOLD: Poids extra-gras
    :cvar EXTRA_BOLD_ITALIC: Poids extra-gras italique
    :cvar BLACK: Poids noir
    :cvar BLACK_ITALIC: Poids noir italique
    """
    THIN = 'Thin' 
    THIN_ITALIC = 'Thin Italic'
    EXTRA_LIGHT = 'ExtraLight'
    EXTRA_LIGHT_ITALIC = 'ExtraLight Italic'
    LIGHT = 'Light'
    LIGHT_ITALIC = 'Light Italic'
    REGULAR = 'Regular'
    ITALIC = 'Italic'
    MEDIUM = 'Medium'
    MEDIUM_ITALIC = 'Medium Italic'
    SEMI_BOLD = 'SemiBold'
    SEMI_BOLD_ITALIC = 'SemiBold Italic'
    BOLD = 'Bold'
    BOLD_ITALIC = 'Bold Italic'
    EXTRA_BOLD = 'ExtraBold'
    EXTRA_BOLD_ITALIC = 'ExtraBold Italic'
    BLACK = 'Black'
    BLACK_ITALIC = 'Black Italic'
