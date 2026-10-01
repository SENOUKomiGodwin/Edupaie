"""
Service de gestion des années scolaires.

Contient la logique métier pour les opérations sur les années scolaires.
"""

from typing import List, Optional, Dict
from data.repositories.annee_repository import AnneeRepository


class AnneeService:
    """Service pour la gestion des années scolaires."""
    
    @staticmethod
    def get_all_annees() -> List[Dict]:
        """
        Récupère toutes les années scolaires.
        
        Returns:
            Liste des années scolaires
        """
        return AnneeRepository.get_all()
    
    @staticmethod
    def get_annee_by_id(annee_id: int) -> Optional[Dict]:
        """
        Récupère une année scolaire par son ID.
        
        Args:
            annee_id: ID de l'année scolaire
            
        Returns:
            Dictionnaire de l'année ou None
        """
        return AnneeRepository.get_by_id(annee_id)
    
    @staticmethod
    def creer_annee(libelle: str) -> int:
        """
        Crée une nouvelle année scolaire avec validation.
        
        Args:
            libelle: Libellé de l'année (ex: "2024-2025")
            
        Returns:
            ID de l'année créée
            
        Raises:
            ValueError: Si les données sont invalides
        """
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de l'année scolaire est obligatoire")
        
        return AnneeRepository.create(libelle.strip())
    
    @staticmethod
    def modifier_annee(annee_id: int, libelle: str) -> bool:
        """
        Modifie une année scolaire avec validation.
        
        Args:
            annee_id: ID de l'année
            libelle: Nouveau libellé
            
        Returns:
            True si succès, False sinon
            
        Raises:
            ValueError: Si les données sont invalides
        """
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de l'année scolaire est obligatoire")
        
        return AnneeRepository.update(annee_id, libelle.strip())
    
    @staticmethod
    def supprimer_annee(annee_id: int) -> bool:
        """
        Supprime une année scolaire.
        
        Args:
            annee_id: ID de l'année
            
        Returns:
            True si succès, False sinon
        """
        return AnneeRepository.delete(annee_id)
