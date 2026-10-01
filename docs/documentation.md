# Documentation Technique - EduPaie

## 1. Architecture de l'application

EduPaie suit une architecture en 3 couches strictement séparées pour garantir la maintenabilité et la testabilité du code.

### 1.1 Couche Data (`data/`)

Cette couche encapsule tout l'accès aux données SQLite.

**Structure :**
```
data/
├── __init__.py
├── database.py          # Connexion et initialisation de la base
├── schema.sql           # Script de création des tables
└── repositories/
    ├── __init__.py
    ├── classe_repository.py      # Opérations sur les classes
    ├── annee_repository.py       # Opérations sur les années
    ├── eleve_repository.py      # Opérations sur les élèves
    └── paiement_repository.py   # Opérations sur les paiements
```

**Responsabilités :**
- Gestion de la connexion SQLite
- Exécution des requêtes SQL paramétrées
- Validation des contraintes d'intégrité
- Aucune logique métier
- Aucune dépendance à PySide6

**Exemple de code :**
```python
class EleveRepository:
    @staticmethod
    def create(nom: str, prenom: str, classe_id: int, annee_id: int, montant_total_du: int) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO eleve (nom, prenom, classe_id, annee_id, montant_total_du)
                VALUES (?, ?, ?, ?, ?)
            """, (nom, prenom, classe_id, annee_id, montant_total_du))
            conn.commit()
            return cursor.lastrowid
```

### 1.2 Couche Services (`services/`)

Cette couche contient la logique métier de l'application.

**Structure :**
```
services/
├── __init__.py
├── eleve_service.py        # Logique métier des élèves
├── paiement_service.py     # Logique métier des paiements
├── classe_service.py        # Logique métier des classes
├── annee_service.py         # Logique métier des années
├── solde_service.py         # Calcul du solde et statut
├── format_service.py        # Formatage des montants et dates
├── validation_service.py    # Validation centralisée
├── dashboard_service.py    # Statistiques du tableau de bord
└── recu_service.py          # Génération des reçus PDF
```

**Responsabilités :**
- Calcul du solde et du statut de paiement
- Validation des données métier
- Formatage des montants en FCFA
- Génération des numéros de reçu
- Aucune dépendance à PySide6
- Utilisation des repositories pour l'accès aux données

**Exemple de code :**
```python
class EleveService:
    @staticmethod
    def creer_eleve(nom: str, prenom: str, classe_id: int, annee_id: int, montant_total_du: int) -> int:
        # Validation via ValidationService
        nom_valide = ValidationService.valider_nom(nom, "Nom")
        montant_valide = ValidationService.valider_montant_entier(montant_total_du, "Montant")
        
        # Vérification de l'existence de la classe et de l'année
        classe = ClasseRepository.get_by_id(classe_id)
        if not classe:
            raise ValidationError("La classe spécifiée n'existe pas")
        
        # Création via repository
        return EleveRepository.create(nom_valide, prenom, classe_id, annee_id, montant_valide)
```

### 1.3 Couche UI (`ui/`)

Cette couche gère l'interface utilisateur avec PySide6.

**Structure :**
```
ui/
├── __init__.py
├── main_window.py                    # Fenêtre principale
├── widgets/
│   ├── __init__.py
│   ├── dashboard_widget.py          # Tableau de bord
│   ├── eleve_list_widget.py         # Liste des élèves
│   ├── eleve_form_widget.py         # Formulaire élève
│   ├── eleve_fiche_widget.py        # Fiche détail élève
│   └── paiement_dialog.py           # Dialogue de paiement
└── models/
    ├── __init__.py
    └── eleve_table_model.py         # Modèle Qt pour la liste
```

**Responsabilités :**
- Affichage des données
- Capture des entrées utilisateur
- Gestion des signaux/slots Qt
- Aucun SQL direct
- Aucune règle métier
- Utilisation des services pour la logique

## 2. Choix Techniques Justifiés

### 2.1 Montants entiers pour le FCFA

**Pourquoi :**
- Le franc CFA n'a pas de centimes
- Évite les erreurs d'arrondi des nombres flottants
- Évite les problèmes de précision binaire (0.1 + 0.2 != 0.3)
- Simplifie les calculs et comparaisons

**Mise en œuvre :**
- `INTEGER` en SQLite
- `int` en Python
- Validation interdisant les décimales
- Fonction `formater_montant()` pour l'affichage

### 2.2 SQLite sans ORM

**Pourquoi :**
- SQL simple et lisible pour un étudiant
- Pas de "magie" de l'ORM
- Compréhension directe des requêtes
- Performance suffisante pour cette application
- Aucune dépendance supplémentaire

**Mise en œuvre :**
- Requêtes paramétrées (jamais de concaténation)
- Transactions explicites pour les écritures
- `PRAGMA foreign_keys = ON` activé
- Index pour optimiser les requêtes fréquentes

### 2.3 PySide6 vs Tkinter/PyQt

**Pourquoi PySide6 :**
- Licence LGPL permissive
- Documentation officielle complète
- Support moderne de Python 3.10+
- Style cohérent sur toutes les plateformes
- Widgets riches et personnalisables

### 2.4 Séparation stricte des couches

**Pourquoi :**
- Testabilité : chaque couche peut être testée indépendamment
- Maintenabilité : modification d'une couche sans impacter les autres
- Lisibilité : responsabilité claire de chaque composant
- Réutilisabilité : services peuvent être réutilisés dans d'autres interfaces (CLI, web)

## 3. Modèle de Données

### 3.1 Schéma Relationnel

```
classe (id, nom UNIQUE)
  ↓
eleve (id, nom, prenom, classe_id FK, annee_id FK, montant_total_du INTEGER)
  ↓
paiement (id, eleve_id FK, montant INTEGER, date_paiement, mode, numero_recu UNIQUE, solde_apres)
```

### 3.2 Contraintes d'Intégrité

- **PRIMARY KEY** : Auto-incrémentée sur toutes les tables
- **FOREIGN KEY** : Avec `PRAGMA foreign_keys = ON`
- **NOT NULL** : Sur tous les champs obligatoires
- **CHECK** : Montants >= 0 pour eleve, > 0 pour paiement
- **UNIQUE** : Nom de classe, libellé d'année, numéro de reçu
- **INDEX** : Sur colonnes fréquemment utilisées (classe_id, annee_id, eleve_id, date_paiement, numero_recu)

### 3.3 Solde Calculé vs Stocké

Le solde est **calculé dynamiquement** : `solde = montant_total_du - SUM(paiements.montant)`

Cependant, `solde_apres` est stocké dans chaque paiement pour :
- Permettre la réimpression identique du reçu
- Tracer l'évolution du solde dans le temps
- Snapshot pour audit

## 4. Gestion des Erreurs

### 4.1 Excepthook Global

Un gestionnaire global des exceptions capture toutes les erreurs non gérées :
- Journalisation dans un fichier de log (`logs/edupaie.log`)
- Affichage d'une boîte de dialogue utilisateur
- Traceback complet disponible pour le débogage

### 4.2 Validation Centralisée

`ValidationService` centralise toutes les validations :
- `valider_nom()` : longueur, caractères
- `valider_montant()` : parsing, positivité, limite
- `valider_date()` : format JJ/MM/AAAA
- `valider_mode_paiement()` : modes autorisés
- Lève `ValidationError` pour les erreurs

### 4.3 Messages Utilisateur

Tous les messages sont en français, clairs et explicites :
- "Le montant doit être un nombre entier positif en FCFA"
- "Le paiement dépasse le solde restant. Solde actuel : 25 000 FCFA"
- "La classe spécifiée n'existe pas"

## 5. Limites Connues

### 5.1 Actuelles
- Pas d'authentification multi-utilisateur
- Pas d'export CSV/Excel des données
- Pas de sauvegarde/restauration automatique
- Pas de configuration de l'école (nom, adresse)
- Pas de gestion des frais supplémentaires
- Pas de rapport financier avancé

### 5.5 Possibles Extensions
- Authentification avec rôles (admin, secrétaire)
- Export des données en CSV/Excel
- Sauvegarde automatique de la base
- Configuration de l'école
- Multi-langue (anglais, etc.)
- Rapports financiers détaillés
- Synchronisation cloud
