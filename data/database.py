"""
Module de connexion et d'initialisation de la base de données SQLite.

Ce module gère la connexion à la base de données et l'initialisation du schéma.
"""

import sqlite3
import sys
import logging
import shutil
from pathlib import Path
from typing import Optional


def resource_path(relative_path):
    """
    Retourne le chemin absolu d'une ressource, fonctionnant aussi avec PyInstaller.

    Args:
        relative_path: Chemin relatif depuis la racine du projet

    Returns:
        Path: Chemin absolu vers la ressource
    """
    if getattr(sys, 'frozen', False):
        # Mode exécutable (PyInstaller)
        base_path = Path(sys._MEIPASS)
    else:
        # Mode développement
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


def get_database_path() -> Path:
    """
    Retourne le chemin vers la base de données.

    La base est stockée dans le dossier utilisateur de l'application,
    accessible en écriture même après packaging avec PyInstaller.

    Returns:
        Path: Chemin vers le fichier de base de données
    """
    # En développement, base dans le répertoire courant
    # En production (PyInstaller), base dans le dossier utilisateur
    if getattr(sys, 'frozen', False):
        # Application packagée
        base_dir = Path.home() / "EduPaie"
    else:
        # Développement
        base_dir = Path(__file__).parent.parent

    base_dir.mkdir(parents=True, exist_ok=True)
    db_path = base_dir / "edupaie.db"

    # Si la base n'existe pas, copier la base embarquée
    if not db_path.exists():
        embedded_db = resource_path("data/edupaie_test.db")
        logging.info(f"Base de données utilisateur introuvable: {db_path}")
        logging.info(f"Copie depuis la base embarquée: {embedded_db}")

        if embedded_db.exists():
            shutil.copy2(embedded_db, db_path)
            logging.info(f"Base de données copiée avec succès")
        else:
            logging.warning(f"Base embarquée introuvable: {embedded_db}")
            # Créer une base vide avec le schéma
            initialize_database()
    else:
        logging.info(f"Base de données existante: {db_path}")

    return db_path


def get_connection() -> sqlite3.Connection:
    """
    Crée et retourne une connexion à la base de données.

    Active les clés étrangères et configure le mode WAL pour améliorer
    la concurrence.

    Returns:
        sqlite3.Connection: Connexion à la base de données
    """
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Accès par nom de colonne
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def initialize_database() -> None:
    """
    Initialise la base de données avec le schéma SQL.

    Lit le fichier schema.sql et exécute les instructions de création
    des tables.
    """
    schema_path = resource_path("data/schema.sql")

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Fichier schéma introuvable : {schema_path}"
        )

    with get_connection() as conn:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        conn.executescript(schema_sql)
        conn.commit()
