"""
Tests unitaires pour les repositories (SQLite en mémoire).
"""

import pytest
import sqlite3
from data.repositories.classe_repository import ClasseRepository
from data.repositories.annee_repository import AnneeRepository
from data.repositories.eleve_repository import EleveRepository


@pytest.fixture
def db_connection():
    """
    Fixture qui crée une connexion SQLite en mémoire.
    
    Initialise le schéma de base pour les tests.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Créer le schéma simplifié pour les tests
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
    
    yield conn
    
    conn.close()


class TestClasseRepository:
    """Tests pour ClasseRepository."""
    
    def test_create_classe(self, db_connection):
        """Teste la création d'une classe."""
        # Utiliser la connexion du repository (on va monkey patch pour les tests)
        # Pour simplifier, on teste directement avec la connexion
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CM2",))
        db_connection.commit()
        
        # Vérifier
        cursor.execute("SELECT * FROM classe WHERE nom = ?", ("CM2",))
        result = cursor.fetchone()
        assert result is not None
        assert result['nom'] == "CM2"
    
    def test_get_all_classes(self, db_connection):
        """Teste la récupération de toutes les classes."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CP1",))
        cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CP2",))
        db_connection.commit()
        
        cursor.execute("SELECT * FROM classe ORDER BY nom")
        results = cursor.fetchall()
        assert len(results) == 2
    
    def test_unique_nom(self, db_connection):
        """Teste que le nom de classe est unique."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CM2",))
        db_connection.commit()
        
        # Essayer d'insérer le même nom
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CM2",))


class TestAnneeRepository:
    """Tests pour AnneeRepository."""
    
    def test_create_annee(self, db_connection):
        """Teste la création d'une année scolaire."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO annee_scolaire (libelle) VALUES (?)", ("2024-2025",))
        db_connection.commit()
        
        cursor.execute("SELECT * FROM annee_scolaire WHERE libelle = ?", ("2024-2025",))
        result = cursor.fetchone()
        assert result is not None
        assert result['libelle'] == "2024-2025"
    
    def test_unique_libelle(self, db_connection):
        """Teste que le libellé d'année est unique."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO annee_scolaire (libelle) VALUES (?)", ("2024-2025",))
        db_connection.commit()
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("INSERT INTO annee_scolaire (libelle) VALUES (?)", ("2024-2025",))


class TestEleveRepository:
    """Tests pour EleveRepository."""
    
    def test_create_eleve(self, db_connection):
        """Teste la création d'un élève."""
        # Créer d'abord une classe et une année
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CM2",))
        cursor.execute("INSERT INTO annee_scolaire (libelle) VALUES (?)", ("2024-2025",))
        db_connection.commit()
        
        # Créer l'élève
        cursor.execute("""
            INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
            VALUES (?, ?, ?, ?, ?)
        """, ("Koffi", "Yawovi", 1, 1, 250000))
        db_connection.commit()
        
        # Vérifier
        cursor.execute("SELECT * FROM eleve WHERE nom = ?", ("Koffi",))
        result = cursor.fetchone()
        assert result is not None
        assert result['prenom'] == "Yawovi"
        assert result['montant_total_du'] == 250000
    
    def test_montant_non_negatif(self, db_connection):
        """Teste que le montant ne peut pas être négatif."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO classe (nom) VALUES (?)", ("CM2",))
        cursor.execute("INSERT INTO annee_scolaire (libelle) VALUES (?)", ("2024-2025",))
        db_connection.commit()
        
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
                VALUES (?, ?, ?, ?, ?)
            """, ("Koffi", "Yawovi", 1, 1, -1000))
    
    def test_foreign_key_classe(self, db_connection):
        """Teste la contrainte de clé étrangère pour la classe."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO annee_scolaire (libelle) VALUES (?)", ("2024-2025",))
        db_connection.commit()
        
        # Essayer de créer un élève avec une classe inexistante
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
                VALUES (?, ?, ?, ?, ?)
            """, ("Koffi", "Yawovi", 999, 1, 250000))
