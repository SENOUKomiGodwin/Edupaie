"""
Repository pour la gestion des élèves.

Encapsule tout l'accès aux données pour la table 'eleve'.
"""

from typing import List, Optional
from data.database import get_connection


class EleveRepository:
    """Repository pour les opérations sur les élèves."""
    
    @staticmethod
    def count() -> int:
        """
        Compte le nombre total d'élèves.
        
        Returns:
            Nombre d'élèves
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM eleve")
            result = cursor.fetchone()
            return result[0] if result else 0
    
    @staticmethod
    def get_total_paye_by_eleve(eleve_id: int) -> int:
        """
        Calcule le total des paiements pour un élève.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            Total payé en FCFA
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(montant), 0) FROM paiement WHERE eleve_id = ?",
                (eleve_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0
    
    @staticmethod
    def get_total_restant_du() -> int:
        """
        Calcule le total restant dû pour tous les élèves.
        
        Returns:
            Total restant dû en FCFA
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(e.montant_total_du - COALESCE(p.total_paye, 0)), 0)
                FROM eleve e
                LEFT JOIN (
                    SELECT eleve_id, SUM(montant) as total_paye
                    FROM paiement
                    GROUP BY eleve_id
                ) p ON e.id = p.eleve_id
            """)
            result = cursor.fetchone()
            return result[0] if result else 0
    
    @staticmethod
    def get_all() -> List[dict]:
        """
        Récupère tous les élèves avec leurs classes et années.
        
        Returns:
            Liste des élèves (dictionnaires)
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.id, e.nom, e.prenom, e.classe_id, e.annee_id,
                       e.montant_total_du, c.nom as classe_nom,
                       a.libelle as annee_libelle
                FROM eleve e
                JOIN classe c ON e.classe_id = c.id
                JOIN annee_scolaire a ON e.annee_id = a.id
                ORDER BY e.nom, e.prenom
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(eleve_id: int) -> Optional[dict]:
        """
        Récupère un élève par son ID.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            Dictionnaire de l'élève ou None
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.id, e.nom, e.prenom, e.classe_id, e.annee_id,
                       e.montant_total_du, c.nom as classe_nom,
                       a.libelle as annee_libelle
                FROM eleve e
                JOIN classe c ON e.classe_id = c.id
                JOIN annee_scolaire a ON e.annee_id = a.id
                WHERE e.id = ?
            """, (eleve_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def search(nom: str, classe_id: Optional[int] = None) -> List[dict]:
        """
        Recherche des élèves par nom et/ou classe.
        
        Args:
            nom: Partie du nom à rechercher
            classe_id: Filtre optionnel par classe
            
        Returns:
            Liste des élèves correspondants
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if classe_id:
                cursor.execute("""
                    SELECT e.id, e.nom, e.prenom, e.classe_id, e.annee_id,
                           e.montant_total_du, c.nom as classe_nom,
                           a.libelle as annee_libelle
                    FROM eleve e
                    JOIN classe c ON e.classe_id = c.id
                    JOIN annee_scolaire a ON e.annee_id = a.id
                    WHERE e.nom LIKE ? AND e.classe_id = ?
                    ORDER BY e.nom, e.prenom
                """, (f"%{nom}%", classe_id))
            else:
                cursor.execute("""
                    SELECT e.id, e.nom, e.prenom, e.classe_id, e.annee_id,
                           e.montant_total_du, c.nom as classe_nom,
                           a.libelle as annee_libelle
                    FROM eleve e
                    JOIN classe c ON e.classe_id = c.id
                    JOIN annee_scolaire a ON e.annee_id = a.id
                    WHERE e.nom LIKE ?
                    ORDER BY e.nom, e.prenom
                """, (f"%{nom}%",))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def create(nom: str, prenom: str, classe_id: int, 
               annee_id: int, montant_total_du: int) -> int:
        """
        Crée un nouvel élève.
        
        Args:
            nom: Nom de l'élève
            prenom: Prénom de l'élève
            classe_id: ID de la classe
            annee_id: ID de l'année scolaire
            montant_total_du: Montant total dû en FCFA
            
        Returns:
            ID de l'élève créé
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
                VALUES (?, ?, ?, ?, ?)
            """, (nom, prenom, classe_id, annee_id, montant_total_du))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update(eleve_id: int, nom: str, prenom: str, 
               classe_id: int, annee_id: int, montant_total_du: int) -> bool:
        """
        Met à jour un élève.
        
        Args:
            eleve_id: ID de l'élève
            nom: Nouveau nom
            prenom: Nouveau prénom
            classe_id: Nouvelle classe
            annee_id: Nouvelle année
            montant_total_du: Nouveau montant total dû
            
        Returns:
            True si succès, False sinon
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE eleve
                SET nom = ?, prenom = ?, classe_id = ?, annee_id = ?, montant_total_du = ?
                WHERE id = ?
            """, (nom, prenom, classe_id, annee_id, montant_total_du, eleve_id))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(eleve_id: int) -> bool:
        """
        Supprime un élève avec transaction explicite.

        Args:
            eleve_id: ID de l'élève

        Returns:
            True si succès

        Raises:
            ValueError: Si des paiements existent pour cet élève
            sqlite3.IntegrityError: Si violation de contrainte
        """
        import sqlite3

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            try:
                # Transaction explicite
                cursor.execute("BEGIN TRANSACTION")

                # Vérifier si l'élève a des paiements
                cursor.execute(
                    "SELECT COUNT(*) FROM paiement WHERE eleve_id = ?",
                    (eleve_id,)
                )
                count = cursor.fetchone()[0]

                if count > 0:
                    raise ValueError(
                        f"Impossible de supprimer : cet élève a {count} paiement(s) enregistré(s)"
                    )

                # Supprimer l'élève
                cursor.execute(
                    "DELETE FROM eleve WHERE id = ?",
                    (eleve_id,)
                )

                if cursor.rowcount == 0:
                    raise ValueError("Élève introuvable")

                conn.commit()
                return True

            except sqlite3.IntegrityError as e:
                conn.rollback()
                raise ValueError(
                    f"Erreur d'intégrité lors de la suppression : {str(e)}"
                )
            except ValueError:
                conn.rollback()
                raise
            except Exception as e:
                conn.rollback()
                raise
