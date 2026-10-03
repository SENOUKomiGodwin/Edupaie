"""
Service de gestion des années scolaires.

Contient la logique métier pour les opérations sur les années scolaires.
"""

from typing import List, Optional, Dict
from datetime import datetime
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
        
        libelle = libelle.strip()
        
        # Validation du format AAAA-AAAA
        if not AnneeService._valider_format_annee(libelle):
            raise ValueError(
                "Le libellé de l'année doit être au format AAAA-AAAA (ex: 2024-2025)"
            )
        
        return AnneeRepository.create(libelle)
    
    @staticmethod
    def _valider_format_annee(libelle: str) -> bool:
        """
        Valide le format du libellé d'année scolaire.
        
        Args:
            libelle: Libellé à valider
            
        Returns:
            True si valide, False sinon
        """
        try:
            # Vérifier le format AAAA-AAAA
            parts = libelle.split("-")
            if len(parts) != 2:
                return False
            
            annee1 = int(parts[0])
            annee2 = int(parts[1])
            
            # Vérifier que la 2ème année = 1ère année + 1
            if annee2 != annee1 + 1:
                return False
            
            # Vérifier que la 1ère année est entre 2000 et année courante + 5
            annee_courante = datetime.now().year
            if annee1 < 2000 or annee1 > annee_courante + 5:
                return False
            
            return True
        except (ValueError, IndexError):
            return False
    
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
        
        libelle = libelle.strip()
        
        # Validation du format AAAA-AAAA
        if not AnneeService._valider_format_annee(libelle):
            raise ValueError(
                "Le libellé de l'année doit être au format AAAA-AAAA (ex: 2024-2025)"
            )
        
        return AnneeRepository.update(annee_id, libelle)
    
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
