"""
Configuration de l'application EduPaie.

Définit la devise (FCFA), les formats de dates et de montants,
et les constantes utilisées dans toute l'application.
"""

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
