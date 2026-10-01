# Plan de Soutenance - EduPaie

## 1. Introduction (1-2 minutes)

**Objectif :** Présenter le contexte et l'objectif du projet.

- **Problème résolu :** Les petites écoles suivent les paiements manuellement (cahier, Excel) sans vue fiable sur les soldes.
- **Solution :** EduPaie, application desktop de gestion des paiements scolaires.
- **Devise :** Franc CFA (FCFA), montants entiers (pas de centimes).
- **Public cible :** Secrétaires d'école sans connaissances techniques.

## 2. Démonstration du produit (8-10 minutes)

### 2.1 Tableau de bord (1 minute)
1. Lancer l'application
2. Montrer le tableau de bord avec les statistiques :
   - Nombre d'élèves
   - Total encaissé
   - Total restant dû
   - Élèves non soldés
3. Expliquer que les données sont en temps réel

### 2.2 Gestion des élèves (3 minutes)
1. **Création d'un élève** :
   - Cliquer sur "Élèves" → "Nouvel élève"
   - Remplir le formulaire (ex: Koffi Yawovi, CM2, 250000 FCFA)
   - Enregistrer et montrer l'élève dans la liste
   - Expliquer la validation des champs

2. **Modification d'un élève** :
   - Sélectionner l'élève créé
   - Cliquer sur "Modifier"
   - Changer le montant total dû
   - Enregistrer

3. **Suppression d'un élève** :
   - Créer un deuxième élève
   - Enregistrer un paiement pour cet élève
   - Tenter de le supprimer → montrer que c'est refusé (car il a des paiements)
   - Expliquer : préservation de l'historique financier

### 2.3 Enregistrement d'un paiement (3 minutes)
1. Sélectionner le premier élève (sans paiements)
2. Cliquer sur "Enregistrer paiement"
3. Montrer le formulaire :
   - Solde restant affiché
   - Montant limité au solde
   - Modes de paiement (Espèces, Chèque, Virement, Mobile money)
4. Enregistrer un paiement partiel (ex: 50 000 FCFA)
5. Montrer :
   - Le reçu PDF généré automatiquement
   - Le solde mis à jour dans la liste
   - Le statut passé de "Non payé" à "Partiellement payé"

6. Enregistrer un second paiement
7. Montrer que le statut devient "Soldé" quand le solde atteint 0

### 2.4 Fiche élève et historique (2 minutes)
1. Cliquer sur "Voir fiche" pour un élève
2. Montrer les informations détaillées :
   - Nom, prénom, classe, année
   - Total dû, solde, statut avec code couleur
3. Montrer l'historique des paiements :
   - Tableau chronologique
   - Numéro de reçu unique pour chaque paiement
   - Solde après chaque paiement
4. Cliquer sur "Ré-imprimer le reçu" pour un paiement
5. Montrer que le PDF est régénéré à l'identique

### 2.5 Recherche et filtres (1 minute)
1. Dans la liste des élèves, utiliser la recherche
2. Rechercher un élève par nom
3. Filtrer par classe
4. Montrer que la liste se met à jour en temps réel

## 3. Aspects Techniques (2-3 minutes)

### 3.1 Architecture (1 minute)
- Montrer la structure du projet dans l'IDE
- Expliquer l'architecture en 3 couches :
  - `data/` : Repositories et SQL
  - `services/` : Logique métier
  - `ui/` : Interface PySide6
- Expliquer la séparation stricte : aucun SQL dans l'UI, aucune logique métier dans les repositories

### 3.2 Base de données (1 minute)
- Ouvrir `docs/schema_mcd.md`
- Montrer le diagramme Mermaid
- Expliquer les tables et les relations
- Expliquer les contraintes : PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE
- Expliquer le choix des montants entiers (pas de centimes pour le FCFA)

### 3.3 Gestion des erreurs (30 secondes)
- Montrer le logging dans `logs/edupaie.log`
- Expliquer l'excepthook global
- Montrer la validation centralisée dans `ValidationService`

## 4. Questions Probables et Réponses

### Q1 : Pourquoi avoir choisi SQLite plutôt qu'une base de données serveur ?
**R :** SQLite est suffisant pour une application desktop monoposte. Pas besoin d'installation de serveur, zéro configuration, fichier portable. Le SQL reste simple et lisible pour l'étudiant.

### Q2 : Pourquoi les montants sont-ils des entiers et pas des décimaux ?
**R :** Le franc CFA n'a pas de centimes. Les entiers évitent les erreurs d'arrondi des nombres flottants (0.1 + 0.2 != 0.3 en binaire). C'est plus simple et plus fiable pour la comptabilité.

### Q3 : Pourquoi avoir séparé en 3 couches ?
**R :** 
- **Testabilité** : Chaque couche peut être testée indépendamment (26 tests unitaires)
- **Maintenabilité** : Modifier l'UI ne casse pas la logique métier
- **Lisibilité** : Responsabilité claire de chaque composant
- **Réutilisabilité** : Les services pourraient être réutilisés pour une interface web ou CLI

### Q4 : Comment garantissez-vous l'unicité des numéros de reçu ?
**R :** Table `sequence_recu` avec l'année comme clé primaire. À chaque génération, on incrémente le compteur. Le numéro est unique et jamais réutilisé, même après suppression d'un paiement.

### Q5 : Pourquoi ne pas permettre la suppression d'un élève avec des paiements ?
**R :** Pour préserver l'historique financier. Supprimer un élève avec des paiements détruirait la traçabilité comptable. On exige une confirmation explicite (non implémenté dans cette version pour simplifier).

### Q6 : Comment sont gérées les erreurs dans l'application ?
**R :** 
- Excepthook global capture toutes les exceptions non gérées
- Journalisation dans un fichier de log
- Boîte de dialogue utilisateur avec message clair
- Validation centralisée avec messages explicites en français
- Aucune exception non gérée ne plante l'application

### Q7 : Pourquoi PySide6 et pas Tkinter ?
**R :** PySide6 est plus moderne, a une meilleure documentation, une licence LGPL permissive, et des widgets plus riches. Tkinter est limité et vieillissant.

### Q8 : Le solde est-il stocké ou calculé ?
**R :** Les deux ! Le solde est calculé dynamiquement (total_du - somme_paiements) pour garantir la cohérence. Mais `solde_apres` est stocké dans chaque paiement pour permettre la réimpression identique du reçu (snapshot).

### Q9 : Comment avez-vous testé l'application ?
**R :** 
- 26 tests unitaires avec pytest
- Tests des services (formatage, validation)
- Tests des repositories (SQLite en mémoire)
- Tests manuels de chaque fonctionnalité
- Jeu de données de test avec 15 élèves et historique varié

### Q10 : Quelles sont les limites de l'application ?
**R :** 
- Pas d'authentification multi-utilisateur
- Pas d'export CSV/Excel
- Pas de sauvegarde automatique
- Pas de configuration de l'école (nom, adresse)
- Pas de rapports financiers avancés
- Ces extensions sont possibles mais hors scope du projet initial

## 5. Conclusion (30 secondes)

- Résumer les 6 fonctionnalités principales
- Insister sur la séparation propre des couches
- Mentionner que le code est lisible et documenté pour être expliqué
- Inviter à tester l'application avec le jeu de données fourni
