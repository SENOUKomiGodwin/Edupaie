"""
Service de gestion des classes.

Contient la logique métier pour les opérations sur les classes.
"""

from typing import List, Optional, Dict
from data.repositories.classe_repository import ClasseRepository


class ClasseService:
    """Service pour la gestion des classes."""
    
    @staticmethod
    def get_all_classes() -> List[Dict]:
        """
        Récupère toutes les classes.
        
        Returns:
            Liste des classes
        """
        return ClasseRepository.get_all()
    
    @staticmethod
    def get_classe_by_id(classe_id: int) -> Optional[Dict]:
        """
        Récupère une classe par son ID.
        
        Args:
            classe_id: ID de la classe
            
        Returns:
            Dictionnaire de la classe ou None
        """
        return ClasseRepository.get_by_id(classe_id)
    
    @staticmethod
    def creer_classe(nom: str) -> int:
        """
        Crée une nouvelle classe avec validation.
        
        Args:
            nom: Nom de la classe
            
        Returns:
            ID de la classe créée
            
        Raises:
            ValueError: Si les données sont invalides
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom de la classe est obligatoire")
        
        return ClasseRepository.create(nom.strip())
    
    @staticmethod
    def modifier_classe(classe_id: int, nom: str) -> bool:
        """
        Modifie une classe avec validation.
        
        Args:
            classe_id: ID de la classe
            nom: Nouveau nom
            
        Returns:
            True si succès, False sinon
            
        Raises:
            ValueError: Si les données sont invalides
        """
        if not nom or not nom.strip():
            raise ValueError("Le nom de la classe est obligatoire")
        
        return ClasseRepository.update(classe_id, nom.strip())
    
    @staticmethod
    def supprimer_classe(classe_id: int) -> bool:
        """
        Supprime une classe.
        
        Args:
            classe_id: ID de la classe
            
        Returns:
            True si succès, False sinon
        """
        return ClasseRepository.delete(classe_id)
