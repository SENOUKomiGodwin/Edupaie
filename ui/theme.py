"""
Thème EduPaie — design clair à accent vert.

Toutes les valeurs du design (couleurs, tailles de police, rayons) sont
définies ici en constantes Python. La feuille de style ui/styles.qss.tpl
utilise des marqueurs ({{VERT}}, {{FOND}}...) substitués par ces constantes
au chargement (voir ui/style_loader.py).

Ne jamais coder de couleur en dur dans les widgets : importer les constantes.
"""

# ------------------------------------------------------------------
# Couleurs de fond et surfaces
# ------------------------------------------------------------------
FOND = "#F6F7F4"            # Fond général de l'application
CARTE = "#FFFFFF"           # Fond des cartes
BORDURE = "#E7E5E4"         # Bordure des cartes
SEPARATEUR = "#F0EEEC"      # Séparateurs discrets, hover neutre
BORDURE_CHAMP = "#D6D3D1"   # Bordure des champs et boutons par défaut

# ------------------------------------------------------------------
# Texte
# ------------------------------------------------------------------
TEXTE = "#1C1917"           # Texte principal
TEXTE_SECOND = "#57534E"    # Texte secondaire
TEXTE_DISCRET = "#78716C"   # Légendes, texte discret

# ------------------------------------------------------------------
# Accent vert (action principale)
# ------------------------------------------------------------------
VERT = "#047857"            # Bouton plein vert, focus des champs
VERT_HOVER = "#065F46"      # Survol / appui du vert
VERT_FOND = "#ECFDF5"       # Fond vert léger (sélection, statut Soldé)

# ------------------------------------------------------------------
# Statuts et alertes
# ------------------------------------------------------------------
ORANGE = "#B45309"          # Statut « Partiellement payé »
ROUGE = "#B91C1C"           # Statut « Non payé », action destructive
ROUGE_BORDURE = "#FCA5A5"   # Bordure du bouton danger
ROUGE_FOND = "#FEF2F2"      # Fond léger du hover danger

# ------------------------------------------------------------------
# Géométrie
# ------------------------------------------------------------------
RAYON_CONTROLE = 8          # Rayon des boutons et champs (px)
RAYON_CARTE = 12            # Rayon des cartes (px)

# ------------------------------------------------------------------
# Typographie (police fixée aussi par code dans style_loader)
# ------------------------------------------------------------------
POLICE = "Segoe UI"
TAILLE_TITRE_PAGE = 20      # Titre de page, graisse 500
TAILLE_CORPS = 13           # Corps de texte
TAILLE_LEGENDE = 11         # Légendes, en-têtes de colonnes

# Graisses autorisées : 400 (normal) et 500 (medium) uniquement.


def couleur_statut(statut: str) -> str:
    """
    Retourne la couleur du texte associée à un statut d'élève.

    Args:
        statut: Libellé du statut (« Soldé », « Partiellement payé », « Non payé »)

    Returns:
        Code hexadécimal de la couleur du statut
    """
    if statut == "Soldé":
        return VERT
    if statut == "Partiellement payé":
        return ORANGE
    return ROUGE
