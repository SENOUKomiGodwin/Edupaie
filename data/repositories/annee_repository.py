"""
Repository pour la gestion des années scolaires.

Encapsule tout l'accès aux données pour la table 'annee_scolaire'.
"""

from typing import List, Optional
from data.database import get_connection


class AnneeRepository:
    """Repository pour les opérations sur les années scolaires."""
    
    @staticmethod
    def get_all() -> List[dict]:
        """
        Récupère toutes les années scolaires.
        
        Returns:
            Liste des années (dictionnaires)
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, libelle FROM annee_scolaire ORDER BY libelle DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(annee_id: int) -> Optional[dict]:
        """
        Récupère une année scolaire par son ID.
        
        Args:
            annee_id: ID de l'année scolaire
            
        Returns:
            Dictionnaire de l'année ou None
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, libelle FROM annee_scolaire WHERE id = ?",
                (annee_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create(libelle: str) -> int:
        """
        Crée une nouvelle année scolaire.
        
        Args:
            libelle: Libellé de l'année (ex: "2025-2026")
            
        Returns:
            ID de l'année créée
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO annee_scolaire (libelle) VALUES (?)",
                (libelle,)
            )
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(annee_id: int, libelle: str) -> bool:
        """
        Met à jour une année scolaire.
        
        Args:
            annee_id: ID de l'année
            libelle: Nouveau libellé
            
        Returns:
            True si succès, False sinon
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE annee_scolaire SET libelle = ? WHERE id = ?",
                (libelle, annee_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(annee_id: int) -> bool:
        """
        Supprime une année scolaire.
        
        Args:
            annee_id: ID de l'année
            
        Returns:
            True si succès, False sinon
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM annee_scolaire WHERE id = ?",
                (annee_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
