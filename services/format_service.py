"""
Service de formatage des montants et dates.

Contient les fonctions pour formater et parser les montants en FCFA.
"""

import re
from config import DEVISE, SEPARATEUR_MILLIERS, FORMAT_DATE


def formater_montant(valeur: int) -> str:
    """
    Formate un montant entier en FCFA avec séparateur de milliers.
    
    Args:
        valeur: Montant en FCFA (entier)
        
    Returns:
        Chaîne formatée (ex: "25 000 FCFA")
        
    Examples:
        >>> formater_montant(25000)
        '25 000 FCFA'
        >>> formater_montant(1500000)
        '1 500 000 FCFA'
    """
    if valeur < 0:
        raise ValueError("Le montant ne peut pas être négatif")
    
    # Convertir en chaîne et insérer les séparateurs de milliers
    chaine = str(valeur)
    parties = []
    
    # Parcourir de droite à gauche par groupes de 3
    for i in range(len(chaine), 0, -3):
        debut = max(0, i - 3)
        parties.insert(0, chaine[debut:i])
    
    montant_formate = SEPARATEUR_MILLIERS.join(parties)
    return f"{montant_formate} {DEVISE}"


def parser_montant(texte: str) -> int:
    """
    Parse une chaîne de texte en montant entier en FCFA.

    Accepte les espaces comme séparateurs de milliers.
    Tolère et retire "FCFA", les espaces normaux, \u00a0 et \u202f.
    Refuse les décimales, les lettres (hors FCFA), les zéros et les négatifs.

    Args:
        texte: Texte à parser (ex: "25 000", "25000", "25 000 FCFA", "25\u202f000")

    Returns:
        Montant entier en FCFA

    Raises:
        ValueError: Si le format est invalide

    Examples:
        >>> parser_montant("25 000")
        25000
        >>> parser_montant("25000")
        25000
        >>> parser_montant("25 000 FCFA")
        25000
    """
    # Nettoyer : strip, remplacement des espaces spéciaux
    texte_nettoye = texte.strip()
    texte_nettoye = texte_nettoye.replace("\u00a0", " ")  # Espace insécable
    texte_nettoye = texte_nettoye.replace("\u202f", " ")  # Espace fine insécable

    # Retirer "FCFA" (insensible à la casse)
    texte_nettoye = texte_nettoye.replace("FCFA", "")
    texte_nettoye = texte_nettoye.replace("fcfa", "")
    texte_nettoye = texte_nettoye.replace("Fcfa", "")

    # Supprimer tous les espaces
    texte_nettoye = texte_nettoye.replace(" ", "").strip()

    # Vérifier que ce sont uniquement des chiffres
    if not texte_nettoye.isdigit():
        raise ValueError(
            "Le montant doit être un nombre entier positif en FCFA"
        )

    # Convertir en entier
    valeur = int(texte_nettoye)

    # Refuser zéro
    if valeur == 0:
        raise ValueError("Le montant ne peut pas être zéro")

    return valeur


def montant_en_lettres(valeur: int) -> str:
    """
    Convertit un montant en toutes lettres en français.
    
    Args:
        valeur: Montant en FCFA
        
    Returns:
        Montant en lettres (ex: "Vingt-cinq mille francs CFA")
        
    Examples:
        >>> montant_en_lettres(25000)
        'Vingt-cinq mille francs CFA'
    """
    if valeur < 0:
        raise ValueError("Le montant ne peut pas être négatif")
    
    if valeur == 0:
        return "Zéro francs CFA"
    
    # Units
    unites = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    
    # Dizaines
    dizaines = ["", "dix", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
    
    # Cas spéciaux 10-19
    cas_speciaux = {
        10: "dix", 11: "onze", 12: "douze", 13: "treize", 14: "quatorze", 15: "quinze",
        16: "seize", 17: "dix-sept", 18: "dix-huit", 19: "dix-neuf"
    }
    
    def convertir_groupe(nombre: int) -> str:
        """Convertit un nombre de 0 à 999 en lettres."""
        if nombre == 0:
            return ""
        
        resultat = []
        
        # Centaines
        centaines = nombre // 100
        reste = nombre % 100
        
        if centaines > 0:
            if centaines == 1:
                resultat.append("cent")
            else:
                resultat.append(unites[centaines] + " cents")
        
        # Dizaines et unités
        if reste > 0:
            if reste < 10:
                resultat.append(unites[reste])
            elif reste < 20:
                resultat.append(cas_speciaux[reste])
            else:
                dizaine = reste // 10
                unite = reste % 10
                
                if dizaine == 7 or dizaine == 9:
                    # Cas soixante-dix et quatre-vingt-dix
                    dizaine -= 1
                    unite += 10
                    if unite == 11:
                        mot = dizaines[dizaine] + "-onze"
                    elif unite == 12:
                        mot = dizaines[dizaine] + "-douze"
                    elif unite == 13:
                        mot = dizaines[dizaine] + "-treize"
                    elif unite == 14:
                        mot = dizaines[dizaine] + "-quatorze"
                    elif unite == 15:
                        mot = dizaines[dizaine] + "-quinze"
                    elif unite == 16:
                        mot = dizaines[dizaine] + "-seize"
                    elif unite == 17:
                        mot = dizaines[dizaine] + "-dix-sept"
                    elif unite == 18:
                        mot = dizaines[dizaine] + "-dix-huit"
                    elif unite == 19:
                        mot = dizaines[dizaine] + "-dix-neuf"
                    else:
                        mot = dizaines[dizaine] + "-" + unites[unite]
                    resultat.append(mot)
                else:
                    if unite == 0:
                        if dizaine == 8:
                            resultat.append("quatre-vingts")
                        else:
                            resultat.append(dizaines[dizaine])
                    elif unite == 1:
                        if dizaine == 8:
                            resultat.append("quatre-vingt-un")
                        else:
                            resultat.append(dizaines[dizaine] + "-et-un")
                    else:
                        resultat.append(dizaines[dizaine] + "-" + unites[unite])
        
        return " ".join(resultat)
    
    if valeur == 1:
        return "Un franc CFA"
    
    resultat = []
    
    # Millions
    millions = valeur // 1_000_000
    reste = valeur % 1_000_000
    
    if millions > 0:
        if millions == 1:
            resultat.append("un million")
        else:
            resultat.append(convertir_groupe(millions) + " millions")
    
    # Milliers
    milliers = reste // 1000
    reste = reste % 1000
    
    if milliers > 0:
        if milliers == 1:
            resultat.append("mille")
        else:
            resultat.append(convertir_groupe(milliers) + " mille")
    
    # Reste
    if reste > 0:
        resultat.append(convertir_groupe(reste))
    
    mot = " ".join(resultat)
    
    # Gestion du pluriel de "franc"
    if valeur > 1:
        return mot + " francs CFA"
    else:
        return mot + " franc CFA"


def formater_date(date_obj) -> str:
    """
    Formate un objet date selon le format français.

    Args:
        date_obj: Objet datetime ou date

    Returns:
        Date formatée (JJ/MM/AAAA)
    """
    return date_obj.strftime(FORMAT_DATE)


def parser_date(valeur) -> str:
    """
    Parse une date en chaîne formatée JJ/MM/AAAA.

    Accepte str, date ou datetime, nettoie les espaces parasites
    (y compris \u00a0 et \u202f) et utilise FORMAT_DATE de config.py.

    Args:
        valeur: str, date ou datetime à parser

    Returns:
        Date formatée (JJ/MM/AAAA)

    Raises:
        ValueError: Si le format est invalide
    """
    from datetime import datetime, date

    # Si c'est déjà une date ou datetime, la formatter
    if isinstance(valeur, (date, datetime)):
        return valeur.strftime(FORMAT_DATE)

    # Sinon, nettoyer la chaîne
    if not isinstance(valeur, str):
        raise ValueError("La date doit être une chaîne, un objet date ou datetime")

    # Nettoyer : strip, remplacement des espaces spéciaux par des espaces normaux
    date_nettoyee = valeur.strip()
    date_nettoyee = date_nettoyee.replace("\u00a0", " ")  # Espace insécable
    date_nettoyee = date_nettoyee.replace("\u202f", " ")  # Espace fine insécable

    # Parser avec le format
    try:
        date_obj = datetime.strptime(date_nettoyee, FORMAT_DATE)
        return date_obj.strftime(FORMAT_DATE)
    except ValueError:
        raise ValueError(f"La date doit être au format {FORMAT_DATE.replace('%', '')}")
