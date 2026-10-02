# Guide d'Installation - EduPaie

## 1. Installation pour le développement

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

1. **Cloner ou télécharger le dépôt**
   ```bash
   git clone <url-du-repo>
   cd EduPaie
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python main.py
   ```

## 2. Création de l'exécutable Windows avec PyInstaller

### Prérequis
- Python 3.10+ installé
- EduPaie cloné et dépendances installées

### Étape 1 : Installer PyInstaller
```bash
pip install pyinstaller
```

### Étape 2 : Construire l'exécutable

Depuis le répertoire racine du projet :

```bash
pyinstaller build/edupaie.spec
```

Cela créera :
- `build/` : fichiers de construction intermédiaires
- `dist/EduPaie.exe` : l'exécutable final

### Étape 4 : Tester l'exécutable

1. Double-cliquez sur `dist/EduPaie.exe`
2. L'application devrait se lancer comme avec `python main.py`
3. La base de données sera créée dans `C:\Users\<votre utilisateur>\EduPaie\edupaie.db`

## 3. Distribution de l'exécutable

### Structure recommandée du dossier de distribution

```
EduPaie/
├── EduPaie.exe          # L'exécutable
├── README.md             # Instructions d'utilisation
├── Manuel_Utilisateur.md  # Guide pour l'utilisateur final
└── logs/                 # Dossier créé automatiquement
    └── edupaie.log       # Fichier de log
```

### Pour l'utilisateur final

1. Copier le dossier `EduPaie/` dans un emplacement permanent
2. Double-cliquer sur `EduPaie.exe`
3. L'application créera automatiquement :
   - La base de données dans `C:\Users\<votre utilisateur>\EduPaie\edupaie.db`
   - Le dossier `logs/` pour les fichiers de log
   - Le dossier où les reçus PDF seront sauvegardés

## 4. Premier lancement et configuration

### Au premier lancement

1. L'application initialise automatiquement la base de données
2. Le schéma SQL est créé (`data/schema.sql`)
3. Les tables vides sont prêtes

### Création des données initiales

Deux options :

**Option A : Via l'interface**
1. Créer les classes (CP1, CP2, CM1, CM2, etc.)
2. Créer l'année scolaire (ex: 2025-2026)
3. Créer les élèves manuellement

**Option B : Via le script de seed**
```bash
python seed_database.py
```
Cela créera automatiquement :
- 10 classes
- 2 années scolaires
- 15 élèves avec noms togolais/ouest-africains
- 25+ paiements avec historique varié

## 5. Mise à jour de l'application

### Pour le développeur

1. Tirer les dernières modifications du dépôt
2. Réinstaller les dépendances si nécessaire : `pip install -r requirements.txt`
3. Relancer : `python main.py`

### Pour l'utilisateur final

1. Télécharger la nouvelle version de `EduPaie.exe`
2. Remplacer l'ancien fichier
3. La base de données est conservée automatiquement

## 6. Sauvegarde et restauration

### Sauvegarde manuelle

1. Localiser le fichier de base de données :
   - Développement : `edupaie.db` dans le répertoire du projet
   - Production : `C:\Users\<votre utilisateur>\EduPaie\edupaie.db`
2. Copier ce fichier dans un emplacement sécurisé (USB, cloud, etc.)

### Restauration

1. Fermer EduPaie
2. Remplacer le fichier `edupaie.db` par la sauvegarde
3. Relancer EduPaie

## 7. Dépannage

### L'exécutable ne se lance pas
- Vérifiez que Windows Defender ne bloque pas l'exécution
- Vérifiez que vous avez les droits d'exécution
- Consultez le fichier `logs/edupaie.log` pour les erreurs

### Erreur de base de données
- Le fichier `edupaie.db` est peut-être corrompu
- Supprimez-le et relancez l'application (elle sera recréée)
- Attention : cela effacera toutes les données !

### Problèmes d'affichage
- Vérifiez que votre écran supporte la résolution minimale (1024x768)
- Vérifiez que Windows est en mode d'affichage standard (pas en mode haute échelle)

## 8. Désinstallation

Pour désinstaller EduPaie :

1. Supprimer le dossier `EduPaie/`
2. Supprimer le dossier de données utilisateur `C:\Users\<votre utilisateur>\EduPaie\`
3. (Optionnel) Supprimer le raccourci sur le bureau
