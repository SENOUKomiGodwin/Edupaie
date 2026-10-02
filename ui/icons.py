"""
Gestionnaire d'icônes Google Fonts (Material Icons) pour EduPaie.

Fournit des icônes vectorielles et typographiques issues de Google Fonts,
garantissant un rendu professionnel et sans aucun emoji.
"""

import logging
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QLabel, QPushButton
from ui.style_loader import resource_path
from ui import theme

FONT_FAMILY = "Material Icons"
_FONT_LOADED = False

# Mapping des noms vers les points de code Unicode de Google Material Icons
CODEPOINTS = {
    "dashboard": "\ue871",          # Tableau de bord
    "school": "\ue80c",             # Logo / École
    "people": "\ue7fb",             # Élèves / Groupe
    "person": "\ue7fd",             # Utilisateur individuel
    "search": "\ue8b6",             # Loupe de recherche
    "add": "\ue145",                # Ajouter / Nouvel élève
    "delete": "\ue872",             # Poubelle / Supprimer
    "edit": "\ue3c9",               # Crayon / Modifier
    "visibility": "\ue8f4",         # Oeil / Voir fiche
    "payment": "\ue8a1",            # Carte / Paiement
    "payments": "\ue8a1",           # Paiements
    "credit_card": "\ue870",        # Carte de crédit
    "print": "\ue8ad",              # Imprimante / Reçu
    "refresh": "\ue5d5",            # Flèche circulaire / Actualiser
    "arrow_back": "\ue5c4",         # Flèche retour
    "expand_more": "\ue5cf",        # Chevron bas déroulant
    "check": "\ue5ca",              # Coche validation
    "warning": "\ue002",            # Triangle alerte
    "error": "\ue000",              # Erreur / Alerte
    "hourglass": "\ue88b",          # Sablier / En attente
    "history": "\ue889",            # Horloge historique
    "close": "\ue5cd",              # Croix fermeture / Annuler
    "save": "\ue161",               # Disquette / Enregistrer
}


def charger_police_icones() -> bool:
    """Charge la police Google Material Icons dans l'application."""
    global _FONT_LOADED
    if _FONT_LOADED:
        return True

    font_path = resource_path("ui/fonts/MaterialIcons-Regular.ttf")
    if not font_path.exists():
        logging.warning(f"Fichier de police Google Fonts introuvable : {font_path}")
        return False

    font_id = QFontDatabase.addApplicationFont(str(font_path))
    if font_id >= 0:
        _FONT_LOADED = True
        logging.info("Police Google Material Icons chargée avec succès")
        return True
    else:
        logging.warning("Échec du chargement de la police Google Material Icons")
        return False


def get_glyph(name: str) -> str:
    """
    Retourne le caractère Unicode correspondant à l'icône Google Fonts.

    Args:
        name: Nom de l'icône (ex: 'dashboard', 'people', 'search')

    Returns:
        str: Caractère Unicode
    """
    charger_police_icones()
    return CODEPOINTS.get(name, "")


def get_icon_font(size: int = 16) -> QFont:
    """Retourne l'objet QFont configuré pour Material Icons."""
    charger_police_icones()
    font = QFont(FONT_FAMILY, size)
    font.setStyleHint(QFont.SansSerif)
    return font


def get_icon(name: str, color: str = None, size: int = 18) -> QIcon:
    """
    Génère un QIcon net basé sur la police Google Fonts.

    Args:
        name: Nom de l'icône
        color: Couleur hexadécimale (ex: '#047857', '#FFFFFF')
        size: Taille de l'icône en pixels

    Returns:
        QIcon: Icône prête à être assignée à un bouton ou action
    """
    charger_police_icones()
    glyph = get_glyph(name)
    if not glyph:
        return QIcon()

    color_val = color if color else theme.TEXTE_SECOND

    # Création d'une pixmap avec support haute résolution (2x)
    scale = 2
    px_size = size * scale
    pixmap = QPixmap(px_size, px_size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    font = QFont(FONT_FAMILY, size * scale)
    painter.setFont(font)
    painter.setPen(QColor(color_val))

    painter.drawText(0, 0, px_size, px_size, Qt.AlignCenter, glyph)
    painter.end()

    pixmap.setDevicePixelRatio(scale)
    return QIcon(pixmap)


def creer_label_icone(name: str, color: str = None, size: int = 16) -> QLabel:
    """
    Crée un QLabel affichant directement l'icône Google Fonts.

    Args:
        name: Nom de l'icône
        color: Couleur hexadécimale
        size: Taille de police de l'icône

    Returns:
        QLabel configuré avec la police Material Icons
    """
    charger_police_icones()
    lbl = QLabel(get_glyph(name))
    lbl.setFont(get_icon_font(size))
    if color:
        lbl.setStyleSheet(f"color: {color}; background: transparent;")
    else:
        lbl.setStyleSheet("background: transparent;")
    lbl.setAlignment(Qt.AlignCenter)
    return lbl
