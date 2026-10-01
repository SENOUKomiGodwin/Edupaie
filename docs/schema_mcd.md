# Modèle Conceptuel de Données (MCD) - EduPaie

## Diagramme Mermaid

```mermaid
erDiagram
    CLASSE ||--o{ ELEVE : "contient"
    ANNEE_SCOLAIRE ||--o{ ELEVE : "concerne"
    ELEVE ||--o{ PAIEMENT : "reçoit"

    CLASSE {
        int id PK
        string nom UK
    }

    ANNEE_SCOLAIRE {
        int id PK
        string libelle UK
    }

    ELEVE {
        int id PK
        string nom
        string prenom
        int classe_id FK
        int annee_id FK
        int montant_total_du CHECK ">= 0"
    }

    PAIEMENT {
        int id PK
        int eleve_id FK
        int montant CHECK "> 0"
        string date_paiement
        string mode CHECK "IN (...)"
        string numero_recu UK
        int solde_apres
    }
```

## Description des tables

### Table `classe`
Stocke les classes de l'école (ex: CP1, CE2, CM1).

- `id` : Clé primaire auto-incrémentée
- `nom` : Nom de la classe, unique (ex: "CM2")

### Table `annee_scolaire`
Stocke les années scolaires (ex: 2023-2024, 2024-2025).

- `id` : Clé primaire auto-incrémentée
- `libelle` : Libellé de l'année, unique (ex: "2024-2025")

### Table `eleve`
Stocke les informations des élèves.

- `id` : Clé primaire auto-incrémentée
- `nom` : Nom de l'élève
- `prenom` : Prénom de l'élève
- `classe_id` : Clé étrangère vers `classe`
- `annee_id` : Clé étrangère vers `annee_scolaire`
- `montant_total_du` : Montant total des frais de scolarité en FCFA (entier, >= 0)

### Table `paiement`
Stocke les paiements effectués par les élèves.

- `id` : Clé primaire auto-incrémentée
- `eleve_id` : Clé étrangère vers `eleve`
- `montant` : Montant payé en FCFA (entier, > 0)
- `date_paiement` : Date du paiement (format JJ/MM/AAAA)
- `mode` : Mode de paiement (especes, cheque, virement, mobile_money)
- `numero_recu` : Numéro unique du reçu (ex: REC-2024-000001)
- `solde_apres` : Solde restant après ce paiement (snapshot pour réimpression)

## Contraintes d'intégrité

- **Clés étrangères** : `PRAGMA foreign_keys = ON` activé
- **NOT NULL** : Tous les champs obligatoires
- **CHECK** : Validation des montants (positifs ou nuls)
- **UNIQUE** : Numéro de reçu unique, nom de classe unique, libellé d'année unique
- **Suppression** : Un élève avec des paiements ne peut pas être supprimé (CASCADE non utilisé pour préserver l'historique)

## Choix de modélisation

### Pourquoi les montants sont des entiers ?
Le franc CFA n'a pas de centimes. Stocker les montants comme des entiers évite :
- Les erreurs d'arrondi des nombres flottants
- Les problèmes de précision (ex: 0.1 + 0.2 != 0.3 en binaire)
- La complexité de gestion des décimales

### Pourquoi solde_apres dans paiement ?
Le solde est calculé dynamiquement (total_du - somme(paiements)), mais nous stockons `solde_apres` dans chaque paiement pour :
- Permettre la réimpression identique du reçu (snapshot du solde au moment du paiement)
- Tracer l'évolution du solde dans le temps

### Pourquoi pas de CASCADE DELETE ?
Nous choisissons d'interdire la suppression d'un élève ayant des paiements pour :
- Préserver l'historique financier
- Éviter la perte de données comptables
- Forcer l'utilisateur à confirmer explicitement la suppression
