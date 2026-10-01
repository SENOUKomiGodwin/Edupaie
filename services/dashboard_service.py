"""
Service de statistiques pour le tableau de bord.

Calcule les statistiques globales de l'application.
"""

from typing import Dict
from data.repositories.eleve_repository import EleveRepository
from data.repositories.paiement_repository import PaiementRepository
from services.paiement_service import PaiementService
from services.format_service import formater_montant
from config import STATUT_SOLDE


class DashboardService:
    """Service pour les statistiques du tableau de bord."""
    
    @staticmethod
    def get_statistiques() -> Dict:
        """
        Calcule toutes les statistiques globales.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        # Nombre d'élèves
        nb_eleves = EleveRepository.count()
        
        # Total encaissé
        total_encaisse = PaiementService.get_total_encaisse()
        
        # Total restant dû
        total_restant = EleveRepository.get_total_restant_du()
        
        # Élèves non soldés
        eleves = EleveRepository.get_all()
        nb_non_soldes = 0
        nb_soldes = 0
        nb_partiels = 0
        
        for eleve in eleves:
            total_paye = EleveRepository.get_total_paye_by_eleve(eleve['id'])
            solde = eleve['montant_total_du'] - total_paye
            
            if solde <= 0:
                nb_soldes += 1
            elif total_paye > 0:
                nb_partiels += 1
            else:
                nb_non_soldes += 1
        
        return {
            'nb_eleves': nb_eleves,
            'total_encaisse': total_encaisse,
            'total_encaisse_formate': formater_montant(total_encaisse),
            'total_restant': total_restant,
            'total_restant_formate': formater_montant(total_restant),
            'nb_non_soldes': nb_non_soldes,
            'nb_soldes': nb_soldes,
            'nb_partiels': nb_partiels
        }
    
    @staticmethod
    def get_eleves_par_statut(statut: str) -> list:
        """
        Récupère les élèves filtrés par statut.
        
        Args:
            statut: Statut à filtrer ('soldé', 'partiel', 'non_payé')
            
        Returns:
            Liste des élèves correspondants
        """
        from services.eleve_service import EleveService
        from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE
        
        eleves = EleveService.get_all_eleves()
        
        if statut == 'soldé':
            return [e for e in eleves if e['statut'] == STATUT_SOLDE]
        elif statut == 'partiel':
            return [e for e in eleves if e['statut'] == STATUT_PARTIEL]
        elif statut == 'non_payé':
            return [e for e in eleves if e['statut'] == STATUT_NON_PAYE]
        else:
            return eleves
