"""
Dialogue de formulaire d'élève.

Formulaire d'ajout/modification d'élève.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt
from services.eleve_service import EleveService
from services.classe_service import ClasseService
from services.annee_service import AnneeService
from services.validation_service import ValidationError
from services.format_service import formater_montant


class EleveFormDialog(QDialog):
    """Dialogue de formulaire d'élève."""
    
    def __init__(self, parent=None, eleve_id=None, default_annee_id=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.default_annee_id = default_annee_id
        self.setWindowTitle("Modifier l'élève" if eleve_id else "Nouvel élève")
        self.setMinimumWidth(400)
        self.setup_ui()
        
        if eleve_id:
            self.charger_eleve()
            # Désactiver le combo en mode modification pour éviter les incohérences
            self.annee_combo.setEnabled(False)
        elif default_annee_id:
            # Sélectionner l'année par défaut et désactiver le combo
            for i in range(self.annee_combo.count()):
                if self.annee_combo.itemData(i) == default_annee_id:
                    self.annee_combo.setCurrentIndex(i)
                    self.annee_combo.setEnabled(False)  # Désactiver le combo
                    break
    
    def setup_ui(self):
        """Configure l'interface du formulaire."""
        layout = QVBoxLayout(self)
        
        # Champs
        form_layout = QVBoxLayout()
        
        # Taille fixe pour les labels pour l'alignement
        label_width = 180
        
        # Nom
        nom_layout = QHBoxLayout()
        nom_label = QLabel("Nom :")
        nom_label.setFixedWidth(label_width)
        nom_layout.addWidget(nom_label)
        self.nom_input = QLineEdit()
        nom_layout.addWidget(self.nom_input)
        form_layout.addLayout(nom_layout)
        
        # Prénom
        prenom_layout = QHBoxLayout()
        prenom_label = QLabel("Prénom :")
        prenom_label.setFixedWidth(label_width)
        prenom_layout.addWidget(prenom_label)
        self.prenom_input = QLineEdit()
        prenom_layout.addWidget(self.prenom_input)
        form_layout.addLayout(prenom_layout)
        
        # Classe
        classe_layout = QHBoxLayout()
        classe_label = QLabel("Classe :")
        classe_label.setFixedWidth(label_width)
        classe_layout.addWidget(classe_label)
        self.classe_combo = QComboBox()
        self.charger_classes()
        classe_layout.addWidget(self.classe_combo)
        form_layout.addLayout(classe_layout)
        
        # Année scolaire
        annee_layout = QHBoxLayout()
        annee_label = QLabel("Année scolaire :")
        annee_label.setFixedWidth(label_width)
        annee_layout.addWidget(annee_label)
        self.annee_combo = QComboBox()
        self.charger_annees()
        annee_layout.addWidget(self.annee_combo)
        form_layout.addLayout(annee_layout)
        
        # Montant total dû
        montant_layout = QHBoxLayout()
        montant_label = QLabel("Montant total dû (FCFA) :")
        montant_label.setFixedWidth(label_width)
        montant_layout.addWidget(montant_label)
        self.montant_input = QSpinBox()
        self.montant_input.setRange(0, 999999999)
        self.montant_input.setSingleStep(1000)
        montant_layout.addWidget(self.montant_input)
        form_layout.addLayout(montant_layout)
        
        layout.addLayout(form_layout)
        
        # Boutons
        buttons = QHBoxLayout()
        btn_save = QPushButton("Enregistrer")
        btn_save.clicked.connect(self.on_enregistrer)
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)
    
    def charger_classes(self):
        """Charge les classes dans le ComboBox."""
        try:
            classes = ClasseService.get_all_classes()
            for classe in classes:
                self.classe_combo.addItem(classe['nom'], classe['id'])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des classes : {e}")
    
    def charger_annees(self):
        """Charge les années scolaires dans le ComboBox."""
        try:
            annees = AnneeService.get_all_annees()
            for annee in annees:
                self.annee_combo.addItem(annee['libelle'], annee['id'])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des années : {e}")
    
    def charger_eleve(self):
        """Charge les données de l'élève à modifier."""
        try:
            eleve = EleveService.get_eleve_by_id(self.eleve_id)
            if eleve:
                self.nom_input.setText(eleve['nom'])
                self.prenom_input.setText(eleve['prenom'])
                self.montant_input.setValue(eleve['montant_total_du'])
                
                # Sélectionner la classe
                index = self.classe_combo.findData(eleve['classe_id'])
                if index >= 0:
                    self.classe_combo.setCurrentIndex(index)
                
                # Sélectionner l'année
                index = self.annee_combo.findData(eleve['annee_id'])
                if index >= 0:
                    self.annee_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de l'élève : {e}")
    
    def on_enregistrer(self):
        """Gère l'enregistrement de l'élève."""
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        classe_id = self.classe_combo.currentData()
        annee_id = self.annee_combo.currentData()
        montant_total_du = self.montant_input.value()
        
        # Validation
        if not nom:
            QMessageBox.warning(self, "Attention", "Le nom est obligatoire")
            return
        
        if not prenom:
            QMessageBox.warning(self, "Attention", "Le prénom est obligatoire")
            return
        
        if classe_id is None:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une classe")
            return
        
        if annee_id is None:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une année scolaire")
            return
        
        try:
            if self.eleve_id:
                # Modification
                succes = EleveService.modifier_eleve(
                    self.eleve_id, nom, prenom, classe_id, annee_id, montant_total_du
                )
                if succes:
                    QMessageBox.information(self, "Succès", "L'élève a été modifié avec succès")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Erreur", "La modification a échoué")
            else:
                # Création
                eleve_id = EleveService.creer_eleve(
                    nom, prenom, classe_id, annee_id, montant_total_du
                )
                QMessageBox.information(self, "Succès", f"L'élève a été créé avec succès (ID: {eleve_id})")
                self.accept()
        except ValidationError as e:
            QMessageBox.warning(self, "Erreur de validation", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur inattendue s'est produite : {e}")
