"""
Chargement de la feuille de style EduPaie.

Lit ui/styles.qss.tpl via resource_path(), remplace les marqueurs {{NOM}}
par les constantes de ui/theme.py, puis applique le QSS à l'application.
"""

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from ui import theme


def resource_path(relative_path: str) -> Path:
    """
    Retourne le chemin absolu d'une ressource, compatible PyInstaller.

    Args:
        relative_path: Chemin relatif depuis la racine du projet

    Returns:
        Path: Chemin absolu vers la ressource
    """
    if getattr(sys, 'frozen', False):
        # Exécutable PyInstaller : ressources extraites dans _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # Mode développement
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


def substituer_marqueurs(qss: str) -> str:
    """
    Remplace les marqueurs {{NOM}} par les constantes correspondantes du thème.

    Args:
        qss: Contenu brut du fichier .qss.tpl

    Returns:
        str: QSS final avec toutes les valeurs substituées

    Raises:
        KeyError: Si un marqueur n'a pas de constante correspondante
    """
    correspondances = {
        "FOND": theme.FOND,
        "CARTE": theme.CARTE,
        "BORDURE": theme.BORDURE,
        "SEPARATEUR": theme.SEPARATEUR,
        "BORDURE_CHAMP": theme.BORDURE_CHAMP,
        "TEXTE": theme.TEXTE,
        "TEXTE_SECOND": theme.TEXTE_SECOND,
        "TEXTE_DISCRET": theme.TEXTE_DISCRET,
        "VERT": theme.VERT,
        "VERT_FONCE": theme.VERT_FONCE,
        "VERT_HOVER": theme.VERT_HOVER,
        "VERT_FOND": theme.VERT_FOND,
        "VERT_CLAIR": theme.VERT_CLAIR,
        "VERT_TEXTE": theme.VERT_TEXTE,
        "BLEU": theme.BLEU,
        "BLEU_FOND": theme.BLEU_FOND,
        "ORANGE": theme.ORANGE,
        "ORANGE_FOND": theme.ORANGE_FOND,
        "ORANGE_BORDURE": theme.ORANGE_BORDURE,
        "ROUGE": theme.ROUGE,
        "ROUGE_BORDURE": theme.ROUGE_BORDURE,
        "ROUGE_FOND": theme.ROUGE_FOND,
        "RAYON_CONTROLE": str(theme.RAYON_CONTROLE),
        "RAYON_CARTE": str(theme.RAYON_CARTE),
        "RAYON_SIDEBAR": str(theme.RAYON_SIDEBAR),
        "RAYON_PILULE": str(theme.RAYON_PILULE),
        "POLICE": theme.POLICE,
        "TAILLE_TITRE_PAGE": str(theme.TAILLE_TITRE_PAGE),
        "TAILLE_SOUS_TITRE": str(theme.TAILLE_SOUS_TITRE),
        "TAILLE_CORPS": str(theme.TAILLE_CORPS),
        "TAILLE_LEGENDE": str(theme.TAILLE_LEGENDE),
        "TAILLE_STAT": str(theme.TAILLE_STAT),
    }

    resultat = qss
    for nom, valeur in correspondances.items():
        resultat = resultat.replace(f"{{{{{nom}}}}}", valeur)

    # Vérifier qu'il ne reste aucun marqueur non résolu
    import re
    restants = re.findall(r"\{\{[A-Z_]+\}\}", resultat)
    if restants:
        raise KeyError(f"Marqueurs QSS sans constante dans theme.py : {restants}")

    return resultat


def charger_style(app: QApplication) -> bool:
    """
    Charge et applique la feuille de style à l'application.

    En cas d'échec (fichier introuvable, marqueur non résolu), journalise
    l'erreur ET affiche une boîte de dialogue : l'application ne continue
    pas en silence.

    Args:
        app: Instance QApplication

    Returns:
        bool: True si le style est appliqué, False sinon
    """
    qss_path = resource_path("ui/styles.qss.tpl")
    logging.info(f"Chemin résolu du QSS : {qss_path}")

    try:
        contenu = qss_path.read_text(encoding="utf-8")
        qss = substituer_marqueurs(contenu)
        app.setStyleSheet(qss)
        logging.info(f"Feuille de style appliquée ({len(qss)} caractères)")
        return True

    except FileNotFoundError:
        logging.exception("Fichier QSS introuvable")
        QMessageBox.critical(
            None,
            "Erreur de style",
            f"Le fichier de style est introuvable :\n{qss_path}\n\n"
            "L'application s'affichera sans style."
        )
        return False

    except (OSError, KeyError) as e:
        logging.exception(f"Erreur lors du chargement de la feuille de style : {e}")
        QMessageBox.critical(
            None,
            "Erreur de style",
            f"Erreur lors du chargement du style :\n{qss_path}\n\n{e}\n\n"
            "L'application s'affichera sans style."
        )
        return False
