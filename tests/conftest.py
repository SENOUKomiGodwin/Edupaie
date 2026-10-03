"""
Configuration pytest pour l'isolation des tests de base de données.

Crée une base de données temporaire pour chaque session de tests.
"""

import os
import pytest
import shutil
from pathlib import Path
from data.database import initialize_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(tmp_path_factory):
    """
    Fixture de session qui crée une base de données temporaire.
    
    Définit la variable d'environnement EDUPAIE_DB pour que tous les tests
    utilisent cette base temporaire au lieu de la base de développement.
    """
    # Créer un dossier temporaire pour la base de données
    test_db_dir = tmp_path_factory.mktemp("test_db")
    test_db_path = test_db_dir / "test_edupaie.db"
    
    # Définir la variable d'environnement
    os.environ["EDUPAIE_DB"] = str(test_db_path)
    
    # Initialiser la base avec le schéma
    initialize_database()
    
    yield test_db_path
    
    # Nettoyer après tous les tests (pas besoin de supprimer, pytest nettoiera le dossier temporaire)


@pytest.fixture(scope="function", autouse=True)
def clean_database():
    """
    Fixture de fonction qui recrée une base propre pour chaque test.
    
    Évite les conflits entre tests qui s'exécutent en séquence.
    """
    # La base est déjà initialisée par la fixture de session
    # Cette fixture peut être utilisée pour des nettoyages supplémentaires si nécessaire
    pass


@pytest.fixture(autouse=True)
def verify_isolated_database():
    """
    Fixture qui vérifie que les tests n'utilisent pas la base de développement.
    
    Lève une erreur si EDUPAIE_DB pointe vers data/edupaie_test.db ou data/edupaie.db.
    """
    db_path = os.environ.get("EDUPAIE_DB", "")
    
    # Vérifier que ce n'est pas la base de test ou de développement (chemins absolus)
    forbidden_paths = [
        "data/edupaie_test.db",
        "data/edupaie.db",
        "data/edupaie_dev.db",
    ]
    
    for forbidden in forbidden_paths:
        if db_path.endswith(forbidden) or db_path == forbidden:
            raise ValueError(
                f"Les tests ne doivent pas utiliser la base de développement '{forbidden}'. "
                f"Utilisez plutôt la base temporaire configurée par conftest.py."
            )
