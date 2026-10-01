# EduPaie

Application desktop de gestion des paiements scolaires pour les petites écoles.

## Description

EduPaie permet d'enregistrer les élèves et leurs paiements, de calculer automatiquement le solde restant dû, et de générer des reçus numérotés pour chaque versement.

Devise : Franc CFA (FCFA)

## Installation

### Prérequis

- Python 3.10 ou supérieur

### Dépendances

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Architecture

L'application suit une architecture en 3 couches strictement séparées :

- **data/** : Accès aux données (SQLite)
- **services/** : Logique métier
- **ui/** : Interface utilisateur (PySide6)

## Documentation

Voir le dossier `docs/` pour la documentation complète et le manuel utilisateur.

## Licence

© 2024 - EduPaie
