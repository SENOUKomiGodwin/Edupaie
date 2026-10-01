-- Schéma de la base de données EduPaie
-- Devise : FCFA (montants entiers)
-- Encodage : UTF-8

-- Activation des clés étrangères
PRAGMA foreign_keys = ON;

-- Table des classes
CREATE TABLE IF NOT EXISTS classe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Table des années scolaires
CREATE TABLE IF NOT EXISTS annee_scolaire (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Table des élèves
CREATE TABLE IF NOT EXISTS eleve (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    classe_id INTEGER NOT NULL,
    annee_id INTEGER NOT NULL,
    montant_total_du INTEGER NOT NULL CHECK (montant_total_du >= 0),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classe_id) REFERENCES classe(id),
    FOREIGN KEY (annee_id) REFERENCES annee_scolaire(id)
);

-- Table des paiements
CREATE TABLE IF NOT EXISTS paiement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id INTEGER NOT NULL,
    montant INTEGER NOT NULL CHECK (montant > 0),
    date_paiement TEXT NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('especes', 'cheque', 'virement', 'mobile_money')),
    numero_recu TEXT NOT NULL UNIQUE,
    solde_apres INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (eleve_id) REFERENCES eleve(id)
);

-- Table de séquence pour les numéros de reçu
CREATE TABLE IF NOT EXISTS sequence_recu (
    annee INTEGER PRIMARY KEY,
    dernier_numero INTEGER NOT NULL DEFAULT 0
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_eleve_classe ON eleve(classe_id);
CREATE INDEX IF NOT EXISTS idx_eleve_annee ON eleve(annee_id);
CREATE INDEX IF NOT EXISTS idx_paiement_eleve ON paiement(eleve_id);
CREATE INDEX IF NOT EXISTS idx_paiement_date ON paiement(date_paiement);
CREATE INDEX IF NOT EXISTS idx_paiement_recu ON paiement(numero_recu);

-- Trigger pour mettre à jour updated_at des élèves
CREATE TRIGGER IF NOT EXISTS update_eleve_timestamp
AFTER UPDATE ON eleve
BEGIN
    UPDATE eleve SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
