"""
Repository pour la gestion des classes.

Encapsule tout l'accès aux données pour la table 'classe'.
"""

from typing import List, Optional
from data.database import get_connection


class ClasseRepository:
    """Repository pour les opérations sur les classes."""
    
    @staticmethod
    def get_all() -> List[dict]:
        """
        Récupère toutes les classes.
        
        Returns:
            Liste des classes (dictionnaires)
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom FROM classe ORDER BY nom")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(classe_id: int) -> Optional[dict]:
        """
        Récupère une classe par son ID.
        
        Args:
            classe_id: ID de la classe
            
        Returns:
            Dictionnaire de la classe ou None
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nom FROM classe WHERE id = ?",
                (classe_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create(nom: str) -> int:
        """
        Crée une nouvelle classe.
        
        Args:
            nom: Nom de la classe
            
        Returns:
            ID de la classe créée
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO classe (nom) VALUES (?)",
                (nom,)
            )
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(classe_id: int, nom: str) -> bool:
        """
        Met à jour une classe.
        
        Args:
            classe_id: ID de la classe
            nom: Nouveau nom
            
        Returns:
            True si succès, False sinon
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE classe SET nom = ? WHERE id = ?",
                (nom, classe_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(classe_id: int) -> bool:
        """
        Supprime une classe.
        
        Args:
            classe_id: ID de la classe
            
        Returns:
            True si succès, False sinon
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM classe WHERE id = ?",
                (classe_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
