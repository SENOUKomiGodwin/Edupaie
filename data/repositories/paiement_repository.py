"""
Repository pour la gestion des paiements.

Encapsule tout l'accès aux données pour la table 'paiement'.
"""

from typing import List, Optional
from data.database import get_connection


class PaiementRepository:
    """Repository pour les opérations sur les paiements."""
    
    @staticmethod
    def get_all() -> List[dict]:
        """
        Récupère tous les paiements.
        
        Returns:
            Liste des paiements (dictionnaires)
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.eleve_id, p.montant, p.date_paiement,
                       p.mode, p.numero_recu, p.solde_apres,
                       e.nom as eleve_nom, e.prenom as eleve_prenom
                FROM paiement p
                JOIN eleve e ON p.eleve_id = e.id
                ORDER BY p.date_paiement DESC, p.id DESC
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(paiement_id: int) -> Optional[dict]:
        """
        Récupère un paiement par son ID.
        
        Args:
            paiement_id: ID du paiement
            
        Returns:
            Dictionnaire du paiement ou None
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.eleve_id, p.montant, p.date_paiement,
                       p.mode, p.numero_recu, p.solde_apres,
                       e.nom as eleve_nom, e.prenom as eleve_prenom
                FROM paiement p
                JOIN eleve e ON p.eleve_id = e.id
                WHERE p.id = ?
            """, (paiement_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_by_eleve(eleve_id: int) -> List[dict]:
        """
        Récupère tous les paiements d'un élève.
        
        Args:
            eleve_id: ID de l'élève
            
        Returns:
            Liste des paiements de l'élève
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, eleve_id, montant, date_paiement,
                       mode, numero_recu, solde_apres
                FROM paiement
                WHERE eleve_id = ?
                ORDER BY date_paiement ASC, id ASC
            """, (eleve_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def create(eleve_id: int, montant: int, date_paiement: str,
               mode: str, numero_recu: str, solde_apres: int) -> int:
        """
        Crée un nouveau paiement.
        
        Args:
            eleve_id: ID de l'élève
            montant: Montant payé en FCFA
            date_paiement: Date du paiement (format JJ/MM/AAAA)
            mode: Mode de paiement
            numero_recu: Numéro unique du reçu
            solde_apres: Solde restant après ce paiement
            
        Returns:
            ID du paiement créé
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO paiement (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_next_recu_number(annee: int) -> int:
        """
        Génère le prochain numéro de reçu pour une année.
        
        Args:
            annee: Année (ex: 2024)
            
        Returns:
            Prochain numéro séquentiel
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Essayer de récupérer le dernier numéro pour cette année
            cursor.execute(
                "SELECT dernier_numero FROM sequence_recu WHERE annee = ?",
                (annee,)
            )
            row = cursor.fetchone()
            
            if row:
                # Incrémenter le numéro existant
                next_num = row[0] + 1
                cursor.execute(
                    "UPDATE sequence_recu SET dernier_numero = ? WHERE annee = ?",
                    (next_num, annee)
                )
            else:
                # Nouvelle année, commencer à 1
                next_num = 1
                cursor.execute(
                    "INSERT INTO sequence_recu (annee, dernier_numero) VALUES (?, ?)",
                    (annee, next_num)
                )
            
            conn.commit()
            return next_num
    
    @staticmethod
    def get_total_encaisse(annee_id: int = None) -> int:
        """
        Calcule le total des paiements encaissés.
        
        Args:
            annee_id: Optionnel, filtre par année scolaire
        
        Returns:
            Total en FCFA
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            if annee_id:
                cursor.execute("""
                    SELECT COALESCE(SUM(p.montant), 0)
                    FROM paiement p
                    JOIN eleve e ON p.eleve_id = e.id
                    WHERE e.annee_id = ?
                """, (annee_id,))
            else:
                cursor.execute("SELECT COALESCE(SUM(montant), 0) FROM paiement")
            result = cursor.fetchone()
            return result[0] if result else 0
