"""
Thème EduPaie — design moderne à accent vert émeraude.

Toutes les valeurs du design (couleurs, tailles de police, rayons) sont
définies ici en constantes Python. La feuille de style ui/styles.qss.tpl
utilise des marqueurs ({{VERT}}, {{FOND}}...) substitués par ces constantes
au chargement (voir ui/style_loader.py).

Ne jamais coder de couleur en dur dans les widgets : importer les constantes.
"""

# ------------------------------------------------------------------
# Couleurs de fond et surfaces
# ------------------------------------------------------------------
FOND = "#F5F6F8"            # Fond général de l'application (gris très doux)
CARTE = "#FFFFFF"           # Fond des cartes blanches
BORDURE = "#E5E7EB"         # Bordure des cartes et conteneurs
SEPARATEUR = "#F3F4F6"      # Séparateurs discrets, hover neutre
BORDURE_CHAMP = "#D1D5DB"   # Bordure des champs et boutons neutres

# ------------------------------------------------------------------
# Texte
# ------------------------------------------------------------------
TEXTE = "#111827"           # Texte principal (noir adouci)
TEXTE_SECOND = "#4B5563"    # Texte secondaire (gris moyen)
TEXTE_DISCRET = "#9CA3AF"   # Légendes, placeholders, mentions discrètes

# ------------------------------------------------------------------
# Accent vert émeraude (action principale, navigation active)
# ------------------------------------------------------------------
VERT = "#047857"            # Bouton plein vert émeraude, sélection
VERT_FONCE = "#065F46"      # Hover du vert émeraude
VERT_HOVER = "#065F46"      # Survol / appui du vert
VERT_FOND = "#ECFDF5"       # Fond vert très léger (lignes sélectionnées, badges)
VERT_CLAIR = "#D1FAE5"      # Fond badge vert pastel
VERT_TEXTE = "#047857"      # Texte vert statut et menu actif

# ------------------------------------------------------------------
# Couleurs d'indicateurs et progression
# ------------------------------------------------------------------
BLEU = "#1D4ED8"            # Accent bleu (si requis)
BLEU_FOND = "#DBEAFE"       # Fond bleu très léger

# ------------------------------------------------------------------
# Statuts et alertes
# ------------------------------------------------------------------
ORANGE = "#B45309"          # Statut « Partiellement payé »
ORANGE_FOND = "#FEF3C7"     # Fond badge orange
ORANGE_BORDURE = "#FCD34D"  # Bordure badge orange

ROUGE = "#B91C1C"           # Statut « Non payé », action supprimer
ROUGE_FOND = "#FEF2F2"      # Fond bouton supprimer / alerte
ROUGE_BORDURE = "#FCA5A5"   # Bordure bouton supprimer

# ------------------------------------------------------------------
# Géométrie
# ------------------------------------------------------------------
RAYON_CONTROLE = 8          # Rayon des boutons et champs (px)
RAYON_CARTE = 12            # Rayon des cartes principales (px)
RAYON_SIDEBAR = 16          # Rayon de la barre latérale (px)
RAYON_PILULE = 20           # Rayon des pilules / chips de filtre (px)

# ------------------------------------------------------------------
# Typographie
# ------------------------------------------------------------------
POLICE = "Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif"
TAILLE_TITRE_PAGE = 22      # Titre de page, graisse 600
TAILLE_SOUS_TITRE = 13      # Sous-titre / breadcrumb
TAILLE_CORPS = 13           # Corps de texte
TAILLE_LEGENDE = 11         # Légendes, en-têtes de colonnes
TAILLE_STAT = 20            # Valeur statistique dans les cartes


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
