"""
Service de gestion des paiements.

Contient la logique métier pour les opérations sur les paiements,
y compris la génération des numéros de reçu.
"""

from typing import List, Optional, Dict
from datetime import datetime
from data.repositories.paiement_repository import PaiementRepository
from data.repositories.eleve_repository import EleveRepository
from services.solde_service import SoldeService
from services.format_service import formater_montant
from services.validation_service import ValidationService, ValidationError
from config import FORMAT_NUMERO_RECUS


class PaiementService:
    """Service pour la gestion des paiements."""
    
    @staticmethod
    def enregistrer_paiement(eleve_id: int, montant,
                            date_paiement, mode: str) -> int:
        """
        Enregistre un nouveau paiement avec validation et numéro de reçu.

        Args:
            eleve_id: ID de l'élève
            montant: Montant payé en FCFA (int ou str)
            date_paiement: Date du paiement (str, date ou datetime)
            mode: Mode de paiement

        Returns:
            ID du paiement créé

        Raises:
            ValidationError: Si le paiement dépasse le solde ou si données invalides
        """
        from services.format_service import parser_date
        import logging

        # Validation des champs - séparation des étapes
        # a) Validation de l'ID
        try:
            eleve_id_valide = ValidationService.valider_id(eleve_id, "ID de l'élève")
        except ValidationError as e:
            raise ValidationError(str(e))

        # b) Validation du montant (accepte int ou str avec FCFA)
        try:
            montant_valide = ValidationService.valider_montant_entier(montant, "Montant")
        except ValidationError as e:
            raise ValidationError(str(e))

        # c) Validation de la date
        try:
            date_valide = ValidationService.valider_date(parser_date(date_paiement), "Date de paiement")
        except ValidationError as e:
            raise ValidationError(str(e))

        # d) Validation du mode de paiement
        try:
            mode_valide = ValidationService.valider_mode_paiement(mode)
        except ValidationError as e:
            raise ValidationError(str(e))
        
        # Récupérer l'élève
        try:
            eleve = EleveRepository.get_by_id(eleve_id_valide)
        except Exception as e:
            logging.exception("Erreur lors de la récupération de l'élève")
            raise ValidationError(f"Erreur lors de la récupération de l'élève : {e}")

        if not eleve:
            raise ValidationError("L'élève spécifié n'existe pas")

        # Calculer le solde actuel
        try:
            total_paye = EleveRepository.get_total_paye_by_eleve(eleve_id_valide)
            solde_actuel = SoldeService.calculer_solde(eleve['montant_total_du'], total_paye)
        except Exception as e:
            logging.exception("Erreur lors du calcul du solde")
            raise ValidationError(f"Erreur lors du calcul du solde : {e}")

        # e) Règle métier : vérifier que le paiement ne dépasse pas le solde
        if SoldeService.verifier_depassement(montant_valide, solde_actuel):
            raise ValidationError(
                f"Le paiement dépasse le solde restant. "
                f"Solde actuel : {formater_montant(solde_actuel)}"
            )

        # Générer le numéro de reçu
        try:
            numero_recu = PaiementService.generer_numero_recu()
        except Exception as e:
            logging.exception("Erreur lors de la génération du numéro de reçu")
            raise ValidationError(f"Erreur lors de la génération du numéro de reçu : {e}")

        # Calculer le nouveau solde
        nouveau_solde = solde_actuel - montant_valide

        # Enregistrer le paiement
        try:
            return PaiementRepository.create(
                eleve_id_valide,
                montant_valide,
                date_valide,
                mode_valide,
                numero_recu,
                nouveau_solde
            )
        except Exception as e:
            logging.exception("Erreur lors de l'enregistrement du paiement")
            raise ValidationError(f"Erreur lors de l'enregistrement du paiement : {e}")
    
    @staticmethod
    def get_paiements_eleve(eleve_id: int) -> List[Dict]:
        """
        Récupère l'historique des paiements d'un élève.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            Liste des paiements chronologiques
        """
        paiements = PaiementRepository.get_by_eleve(eleve_id)
        
        # Ajouter le mode de paiement en texte
        from config import MODES_PAIEMENT
        for paiement in paiements:
            paiement['mode_texte'] = MODES_PAIEMENT.get(paiement['mode'], paiement['mode'])
            paiement['montant_formate'] = formater_montant(paiement['montant'])
            paiement['solde_formate'] = formater_montant(paiement['solde_apres'])
        
        return paiements
    
    @staticmethod
    def generer_numero_recu() -> str:
        """
        Génère un numéro de reçu unique.
        
        Format: REC-AAAA-000001
        
        Returns:
            Numéro de reçu unique
        """
        annee = datetime.now().year
        numero = PaiementRepository.get_next_recu_number(annee)
        return FORMAT_NUMERO_RECUS.format(annee=annee, numero=numero)
    
    @staticmethod
    def get_total_encaisse(annee_id: int = None) -> int:
        """
        Calcule le total des paiements encaissés.
        
        Args:
            annee_id: Optionnel, filtre par année scolaire
        
        Returns:
            Total en FCFA
        """
        return PaiementRepository.get_total_encaisse(annee_id)
