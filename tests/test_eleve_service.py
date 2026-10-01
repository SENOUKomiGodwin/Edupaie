"""
Tests unitaires pour le service d'élèves, notamment la suppression.
"""

import pytest
import sqlite3
from unittest.mock import patch
from data.repositories.eleve_repository import EleveRepository
from services.eleve_service import EleveService
from services.validation_service import ValidationError


@pytest.fixture
def mock_db():
    """
    Fixture qui mocke la connexion de base de données.
    """
    with patch('data.repositories.eleve_repository.get_connection') as mock:
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        # Créer le schéma
        conn.execute("""
            CREATE TABLE classe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE annee_scolaire (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libelle TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE eleve (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                classe_id INTEGER NOT NULL,
                annee_id INTEGER NOT NULL,
                montant_total_du INTEGER NOT NULL CHECK (montant_total_du >= 0),
                FOREIGN KEY (classe_id) REFERENCES classe(id),
                FOREIGN KEY (annee_id) REFERENCES annee_scolaire(id)
            )
        """)

        conn.execute("""
            CREATE TABLE paiement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                eleve_id INTEGER NOT NULL,
                montant INTEGER NOT NULL CHECK (montant > 0),
                date_paiement TEXT NOT NULL,
                mode TEXT NOT NULL CHECK (mode IN ('especes', 'cheque', 'virement', 'mobile_money')),
                numero_recu TEXT NOT NULL UNIQUE,
                solde_apres INTEGER NOT NULL,
                FOREIGN KEY (eleve_id) REFERENCES eleve(id)
            )
        """)

        # Données de test
        conn.execute("INSERT INTO classe (nom) VALUES ('CM2')")
        conn.execute("INSERT INTO annee_scolaire (libelle) VALUES ('2024-2025')")
        conn.commit()

        mock.return_value.__enter__.return_value = conn
        yield conn
        conn.close()


class TestSuppressionEleve:
    """Tests pour la suppression d'élèves."""

    def test_supprimer_eleve_sans_paiement(self, mock_db):
        """Teste la suppression d'un élève sans paiement."""
        # Créer un élève
        cursor = mock_db.cursor()
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES ('Koffi', 'Yawovi', 1, 1, 250000)
        """)
        mock_db.commit()
        eleve_id = cursor.lastrowid

        # Supprimer l'élève
        result = EleveRepository.delete(eleve_id)
        assert result is True

        # Vérifier que l'élève n'existe plus
        cursor.execute("SELECT * FROM eleve WHERE id = ?", (eleve_id,))
        assert cursor.fetchone() is None

    def test_supprimer_eleve_avec_paiements_refuse(self, mock_db):
        """Teste que la suppression est refusée si l'élève a des paiements."""
        # Créer un élève
        cursor = mock_db.cursor()
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES ('Koffi', 'Yawovi', 1, 1, 250000)
        """)
        mock_db.commit()
        eleve_id = cursor.lastrowid

        # Ajouter un paiement
        cursor.execute("""
            INSERT INTO paiement (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres)
            VALUES (?, 50000, '01/09/2024', 'especes', 'REC-2024-000001', 200000)
        """, (eleve_id,))
        mock_db.commit()

        # Tenter de supprimer l'élève
        with pytest.raises(ValueError) as exc:
            EleveRepository.delete(eleve_id)
        assert "paiement" in str(exc.value).lower()

        # Vérifier que l'élève existe toujours
        cursor.execute("SELECT * FROM eleve WHERE id = ?", (eleve_id,))
        assert cursor.fetchone() is not None

    def test_supprimer_eleve_inexistant(self, mock_db):
        """Teste la suppression d'un élève inexistant."""
        with pytest.raises(ValueError) as exc:
            EleveRepository.delete(999)
        assert "introuvable" in str(exc.value).lower()

    def test_supprimer_eleve_service_sans_paiement(self, mock_db):
        """Teste la suppression via le service pour un élève sans paiement."""
        # Créer un élève
        cursor = mock_db.cursor()
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES ('Koffi', 'Yawovi', 1, 1, 250000)
        """)
        mock_db.commit()
        eleve_id = cursor.lastrowid

        # Supprimer via le service
        result = EleveService.supprimer_eleve(eleve_id)
        assert result is True

        # Vérifier
        cursor.execute("SELECT * FROM eleve WHERE id = ?", (eleve_id,))
        assert cursor.fetchone() is None

    def test_supprimer_eleve_service_avec_paiements(self, mock_db):
        """Teste que le service refuse la suppression avec paiements."""
        # Créer un élève
        cursor = mock_db.cursor()
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES ('Koffi', 'Yawovi', 1, 1, 250000)
        """)
        mock_db.commit()
        eleve_id = cursor.lastrowid

        # Ajouter un paiement
        cursor.execute("""
            INSERT INTO paiement (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres)
            VALUES (?, 50000, '01/09/2024', 'especes', 'REC-2024-000001', 200000)
        """, (eleve_id,))
        mock_db.commit()

        # Tenter de supprimer via le service
        with pytest.raises(ValidationError) as exc:
            EleveService.supprimer_eleve(eleve_id)
        assert "paiement" in str(exc.value).lower()

    def test_supprimer_eleve_service_inexistant(self, mock_db):
        """Teste que le service refuse la suppression d'un élève inexistant."""
        with pytest.raises(ValidationError) as exc:
            EleveService.supprimer_eleve(999)
        assert "n'existe pas" in str(exc.value).lower()

    def test_numero_recu_non_reutilise(self, mock_db):
        """Teste que le numéro de reçu n'est jamais réutilisé après suppression."""
        # Créer un élève
        cursor = mock_db.cursor()
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES ('Koffi', 'Yawovi', 1, 1, 250000)
        """)
        mock_db.commit()
        eleve_id = cursor.lastrowid

        # Ajouter un paiement
        cursor.execute("""
            INSERT INTO paiement (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres)
            VALUES (?, 50000, '01/09/2024', 'especes', 'REC-2024-000001', 200000)
        """, (eleve_id,))
        mock_db.commit()

        # Supprimer l'élève (devrait échouer à cause du paiement)
        with pytest.raises(ValueError):
            EleveRepository.delete(eleve_id)

        # Créer un autre élève
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES ('Mensah', 'Komi', 1, 1, 300000)
        """)
        mock_db.commit()
        eleve_id2 = cursor.lastrowid

        # Ajouter un paiement pour le nouvel élève
        cursor.execute("""
            INSERT INTO paiement (eleve_id, montant, date_paiement, mode, numero_recu, solde_apres)
            VALUES (?, 75000, '02/09/2024', 'especes', 'REC-2024-000002', 225000)
        """, (eleve_id2,))
        mock_db.commit()

        # Vérifier que le numéro REC-2024-000001 n'est pas réutilisé
        cursor.execute("SELECT numero_recu FROM paiement ORDER BY id")
        numeros = [row[0] for row in cursor.fetchall()]
        assert "REC-2024-000001" in numeros
        assert "REC-2024-000002" in numeros
        assert len(numeros) == 2
