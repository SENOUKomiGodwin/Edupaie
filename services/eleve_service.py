"""
Service de gestion des élèves.

Contient la logique métier pour les opérations sur les élèves.
"""

from typing import List, Optional, Dict
from data.repositories.eleve_repository import EleveRepository
from data.repositories.classe_repository import ClasseRepository
from data.repositories.annee_repository import AnneeRepository
from services.solde_service import SoldeService
from services.format_service import formater_montant
from services.validation_service import ValidationService, ValidationError


class EleveService:
    """Service pour la gestion des élèves."""
    
    @staticmethod
    def get_all_eleves(annee_id: Optional[int] = None) -> List[Dict]:
        """
        Récupère tous les élèves avec leur solde et statut.
        
        Args:
            annee_id: Si fourni, filtre les élèves par année scolaire
        
        Returns:
            Liste des élèves avec informations calculées
        """
        if annee_id:
            eleves = EleveRepository.get_by_annee(annee_id)
        else:
            eleves = EleveRepository.get_all()
        
        for eleve in eleves:
            total_paye = EleveRepository.get_total_paye_by_eleve(eleve['id'])
            solde = SoldeService.calculer_solde(eleve['montant_total_du'], total_paye)
            statut = SoldeService.determiner_statut(solde, total_paye)
            
            eleve['solde'] = solde
            eleve['total_paye'] = total_paye
            eleve['statut'] = statut
            eleve['solde_formate'] = formater_montant(solde)
            eleve['total_formate'] = formater_montant(eleve['montant_total_du'])
        
        return eleves
    
    @staticmethod
    def get_eleve_by_id(eleve_id: int) -> Optional[Dict]:
        """
        Récupère un élève avec son solde et statut.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            Dictionnaire de l'élève ou None
        """
        eleve = EleveRepository.get_by_id(eleve_id)
        
        if not eleve:
            return None
        
        total_paye = EleveRepository.get_total_paye_by_eleve(eleve_id)
        solde = SoldeService.calculer_solde(eleve['montant_total_du'], total_paye)
        statut = SoldeService.determiner_statut(solde, total_paye)
        
        eleve['solde'] = solde
        eleve['total_paye'] = total_paye
        eleve['statut'] = statut
        eleve['solde_formate'] = formater_montant(solde)
        eleve['total_formate'] = formater_montant(eleve['montant_total_du'])
        
        return eleve
    
    @staticmethod
    def rechercher_eleves(nom: str, classe_id: Optional[int] = None) -> List[Dict]:
        """
        Recherche des élèves avec leur solde et statut.
        
        Args:
            nom: Partie du nom à rechercher
            classe_id: Filtre optionnel par classe
            
        Returns:
            Liste des élèves correspondants
        """
        eleves = EleveRepository.search(nom, classe_id)
        
        for eleve in eleves:
            total_paye = EleveRepository.get_total_paye_by_eleve(eleve['id'])
            solde = SoldeService.calculer_solde(eleve['montant_total_du'], total_paye)
            statut = SoldeService.determiner_statut(solde, total_paye)
            
            eleve['solde'] = solde
            eleve['total_paye'] = total_paye
            eleve['statut'] = statut
            eleve['solde_formate'] = formater_montant(solde)
            eleve['total_formate'] = formater_montant(eleve['montant_total_du'])
        
        return eleves
    
    @staticmethod
    def creer_eleve(nom: str, prenom: str, classe_id: int,
                    annee_id: int, montant_total_du: int) -> int:
        """
        Crée un nouvel élève avec validation.
        
        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe_id: ID de la classe
            annee_id: ID de l'année scolaire
            montant_total_du: Montant total dû en FCFA
            
        Returns:
            ID de l'élève créé
            
        Raises:
            ValidationError: Si les données sont invalides
        """
        # Validation des champs
        nom_valide = ValidationService.valider_nom(nom, "Nom")
        prenom_valide = ValidationService.valider_nom(prenom, "Prénom")
        montant_valide = ValidationService.valider_montant_entier(montant_total_du, "Montant total dû")
        classe_valide = ValidationService.valider_id(classe_id, "ID de la classe")
        annee_valide = ValidationService.valider_id(annee_id, "ID de l'année scolaire")
        
        # Vérifier que la classe existe
        classe = ClasseRepository.get_by_id(classe_valide)
        if not classe:
            raise ValidationError("La classe spécifiée n'existe pas")
        
        # Vérifier que l'année scolaire existe
        annee = AnneeRepository.get_by_id(annee_valide)
        if not annee:
            raise ValidationError("L'année scolaire spécifiée n'existe pas")
        
        return EleveRepository.create(
            nom_valide,
            prenom_valide,
            classe_valide,
            annee_valide,
            montant_valide
        )
    
    @staticmethod
    def modifier_eleve(eleve_id: int, nom: str, prenom: str,
                       classe_id: int, annee_id: int, montant_total_du: int) -> bool:
        """
        Modifie un élève avec validation.
        
        Args:
            eleve_id: ID de l'élève
            nom: Nouveau nom
            prenom: Nouveau prénom
            classe_id: Nouvelle classe
            annee_id: Nouvelle année
            montant_total_du: Nouveau montant total dû
            
        Returns:
            True si succès, False sinon
            
        Raises:
            ValidationError: Si les données sont invalides
        """
        # Validation des champs
        eleve_id_valide = ValidationService.valider_id(eleve_id, "ID de l'élève")
        nom_valide = ValidationService.valider_nom(nom, "Nom")
        prenom_valide = ValidationService.valider_nom(prenom, "Prénom")
        montant_valide = ValidationService.valider_montant_entier(montant_total_du, "Montant total dû")
        classe_valide = ValidationService.valider_id(classe_id, "ID de la classe")
        annee_valide = ValidationService.valider_id(annee_id, "ID de l'année scolaire")
        
        # Vérifier que l'élève existe
        eleve = EleveRepository.get_by_id(eleve_id_valide)
        if not eleve:
            raise ValidationError("L'élève spécifié n'existe pas")
        
        # Vérifier que la classe existe
        classe = ClasseRepository.get_by_id(classe_valide)
        if not classe:
            raise ValidationError("La classe spécifiée n'existe pas")
        
        # Vérifier que l'année scolaire existe
        annee = AnneeRepository.get_by_id(annee_valide)
        if not annee:
            raise ValidationError("L'année scolaire spécifiée n'existe pas")
        
        return EleveRepository.update(
            eleve_id_valide,
            nom_valide,
            prenom_valide,
            classe_valide,
            annee_valide,
            montant_valide
        )
    
    @staticmethod
    def supprimer_eleve(eleve_id: int) -> bool:
        """
        Supprime un élève avec vérification des paiements.

        Args:
            eleve_id: ID de l'élève

        Returns:
            True si succès

        Raises:
            ValidationError: Si des paiements existent ou si l'élève n'existe pas
        """
        # Validation de l'ID
        eleve_id_valide = ValidationService.valider_id(eleve_id, "ID de l'élève")

        # Vérifier que l'élève existe
        eleve = EleveRepository.get_by_id(eleve_id_valide)
        if not eleve:
            raise ValidationError("L'élève spécifié n'existe pas")

        try:
            return EleveRepository.delete(eleve_id_valide)
        except ValueError as e:
            raise ValidationError(str(e))
