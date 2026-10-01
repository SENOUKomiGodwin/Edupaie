# Manuel Utilisateur - EduPaie

## 1. Enregistrer un nouvel élève

### Étape 1 : Accéder à l'écran des élèves
1. Lancez l'application EduPaie
2. Dans la barre latérale, cliquez sur "Élèves"
3. Cliquez sur le bouton "Nouvel élève"

### Étape 2 : Remplir le formulaire
1. **Nom** : Entrez le nom de famille de l'élève (ex: Koffi)
2. **Prénom** : Entrez le prénom de l'élève (ex: Yawovi)
3. **Classe** : Sélectionnez la classe dans la liste déroulante (ex: CM2)
4. **Année scolaire** : Sélectionnez l'année scolaire (ex: 2024-2025)
5. **Montant total dû** : Entrez le montant total des frais de scolarité en FCFA (ex: 250000)

### Étape 3 : Enregistrer
1. Cliquez sur le bouton "Enregistrer"
2. Un message de confirmation apparaît
3. L'élève est ajouté à la liste

## 2. Enregistrer un paiement

### Étape 1 : Sélectionner l'élève
1. Dans la liste des élèves, cliquez sur l'élève concerné
2. Cliquez sur le bouton "Enregistrer paiement"

### Étape 2 : Remplir le formulaire de paiement
1. **Informations élève** : Le nom, la classe et le solde restant sont affichés
2. **Montant** : Entrez le montant du versement en FCFA (ex: 50000)
   - Le montant ne peut pas dépasser le solde restant
3. **Date** : Sélectionnez la date du paiement (par défaut : aujourd'hui)
4. **Mode de paiement** : Choisissez le mode :
   - Espèces
   - Chèque
   - Virement
   - Mobile money (Flooz / T-Money)

### Étape 3 : Valider
1. Cliquez sur "Valider"
2. Le paiement est enregistré
3. Le reçu PDF est généré automatiquement
4. Le solde de l'élève est mis à jour

## 3. Consulter la fiche d'un élève

### Étape 1 : Accéder à la fiche
1. Dans la liste des élèves, cliquez sur l'élève
2. Cliquez sur le bouton "Voir fiche"

### Étape 2 : Informations affichées
- **Informations élève** : Nom, prénom, classe, année scolaire
- **Informations financières** : Total dû, solde restant, statut
- **Statut** : 
  - 🟢 Soldé (solde = 0)
  - 🟡 Partiellement payé (paiements en cours)
  - 🔴 Non payé (aucun paiement)

### Étape 3 : Historique des paiements
- Tableau chronologique de tous les paiements
- Pour chaque paiement : date, montant, mode, numéro de reçu, solde après

### Étape 4 : Ré-imprimer un reçu
1. Dans l'historique, cliquez sur un paiement
2. Cliquez sur "Ré-imprimer le reçu"
3. Le PDF est généré et ouvert automatiquement

## 4. Modifier les informations d'un élève

### Étape 1 : Sélectionner l'élève
1. Dans la liste des élèves, cliquez sur l'élève à modifier
2. Cliquez sur le bouton "Modifier"

### Étape 2 : Modifier les informations
1. Modifiez les champs nécessaires (nom, prénom, classe, année, montant)
2. Cliquez sur "Enregistrer"

## 5. Supprimer un élève

### Étape 1 : Sélectionner l'élève
1. Dans la liste des élèves, cliquez sur l'élève à supprimer
2. Cliquez sur le bouton "Supprimer"

### Étape 2 : Confirmer
1. Une boîte de confirmation apparaît
2. Cliquez sur "Oui" pour confirmer

**Important :** Si l'élève a des paiements enregistrés, la suppression sera refusée pour préserver l'historique financier.

## 6. Tableau de bord

### Accès
Cliquez sur "Tableau de bord" dans la barre latérale.

### Statistiques affichées
- **Nombre d'élèves** : Total d'élèves enregistrés
- **Total encaissé** : Somme de tous les paiements en FCFA
- **Total restant dû** : Somme des soldes restants en FCFA
- **Élèves non soldés** : Nombre d'élèves qui n'ont pas payé en totalité

### Filtrage
- Utilisez le filtre "Filtrer par statut" pour voir :
  - Tous les élèves
  - Seulement les élèves soldés
  - Seulement les élèves partiellement payés
  - Seulement les élèves non payés

## 7. Raccourcis clavier

- **Ctrl+N** : Nouvel élève (lorsque sur l'écran Élèves)
- **Ctrl+F** : Recherche (lorsque sur l'écran Élèves)

## 8. Dépannage

### Problème : "L'application ne se lance pas"
- Vérifiez que Python 3.10+ est installé
- Vérifiez que les dépendances sont installées : `pip install -r requirements.txt`

### Problème : "Erreur lors de l'enregistrement d'un paiement"
- Vérifiez que le montant ne dépasse pas le solde restant
- Vérifiez que la date est au format JJ/MM/AAAA

### Problème : "Impossible de supprimer un élève"
- L'élève a probablement des paiements enregistrés
- Pour supprimer, il faut d'abord supprimer ses paiements (non implémenté dans cette version)

### Problème : "Le reçu PDF ne s'ouvre pas"
- Vérifiez que vous avez un lecteur PDF installé
- Le fichier est sauvegardé dans le dossier de l'application
