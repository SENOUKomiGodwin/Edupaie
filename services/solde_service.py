"""
Service de calcul du solde et du statut de paiement.

Contient la logique métier pour calculer le solde restant
et déterminer le statut de paiement d'un élève.
"""

from typing import Dict, Optional
from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE


class SoldeService:
    """Service pour les calculs de solde."""
    
    @staticmethod
    def calculer_solde(montant_total_du: int, total_paye: int) -> int:
        """
        Calcule le solde restant dû.
        
        Args:
            montant_total_du: Montant total dû en FCFA
            total_paye: Total déjà payé en FCFA
            
        Returns:
            Solde restant en FCFA (peut être négatif si surpaiement)
        """
        return montant_total_du - total_paye
    
    @staticmethod
    def determiner_statut(solde: int, total_paye: int) -> str:
        """
        Détermine le statut de paiement.
        
        Args:
            solde: Solde restant en FCFA
            total_paye: Total payé en FCFA
            
        Returns:
            Statut : "Soldé", "Partiellement payé" ou "Non payé"
        """
        if solde <= 0:
            return STATUT_SOLDE
        elif total_paye > 0:
            return STATUT_PARTIEL
        else:
            return STATUT_NON_PAYE
    
    @staticmethod
    def verifier_depassement(montant_paiement: int, solde_actuel: int) -> bool:
        """
        Vérifie si un paiement dépasse le solde restant.
        
        Args:
            montant_paiement: Montant du paiement proposé
            solde_actuel: Solde restant actuel
            
        Returns:
            True si le paiement dépasse le solde, False sinon
        """
        return montant_paiement > solde_actuel
