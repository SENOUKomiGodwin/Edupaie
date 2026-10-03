"""
Configuration de l'application EduPaie.

Définit la devise (FCFA), les formats de dates et de montants,
et les constantes utilisées dans toute l'application.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Devise
DEVISE = "FCFA"
CODE_ISO_DEVISE = "XOF"

# Formatage des montants
SEPARATEUR_MILLIERS = " "

# Formatage des dates
FORMAT_DATE = "%d/%m/%Y"

# Modes de paiement autorisés
MODES_PAIEMENT = {
    "especes": "Espèces",
    "cheque": "Chèque",
    "virement": "Virement",
    "mobile_money": "Mobile money"
}

# Statuts de paiement
STATUT_SOLDE = "Soldé"
STATUT_PARTIEL = "Partiellement payé"
STATUT_NON_PAYE = "Non payé"

# Format du numéro de reçu
FORMAT_NUMERO_RECUS = "REC-{annee}-{numero:06d}"

# Nom de l'application
APP_NAME = "EduPaie"
APP_VERSION = "1.0.0"

# Coordonnées de l'école
ADRESSE_ECOLE = "Adakpamé , Lomé"
NOM_ECOLE = "Lycée Emraudes"
TEL_ECOLE = "+228 00 00 00 00"


def get_database_path() -> str:
    """
    Retourne le chemin de la base de données depuis la variable d'environnement EDUPAIE_DB.
    
    Si EDUPAIE_DB n'est pas définie, utilise le chemin par défaut (dev ou prod).
    
    Returns:
        str: Chemin vers la base de données
    """
    if "EDUPAIE_DB" in os.environ:
        return os.environ["EDUPAIE_DB"]
    
    # Chemin par défaut selon le contexte
    if getattr(sys, 'frozen', False):
        # Application packagée : dossier utilisateur
        return str(Path.home() / "EduPaie" / "edupaie.db")
    else:
        # Développement : edupaie_dev.db (pas edupaie_test.db qui est le modèle)
        return "data/edupaie_dev.db"