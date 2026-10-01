"""
Widget de fiche élève.

Affiche les détails d'un élève, son solde, son statut et l'historique des paiements.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE


class EleveFicheWidget(QWidget):
    """Widget de fiche élève."""
    
    # Signal pour ré-imprimer un reçu
    reimprimer_recu = Signal(int)  # ID du paiement
    
    # Signal pour fermer la fiche
    fermer_fiche = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.eleve_id = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface de la fiche."""
        layout = QVBoxLayout(self)
        
        # Informations de l'élève
        self.info_layout = self.create_info_section()
        layout.addLayout(self.info_layout)
        
        layout.addSpacing(20)
        
        # Section historique des paiements
        layout.addWidget(QLabel("<b>Historique des paiements</b>"))
        
        # Tableau des paiements
        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(5)
        self.table_paiements.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "N° Reçu", "Solde après"
        ])
        self.table_paiements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_paiements.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_paiements.setSelectionMode(QTableWidget.SingleSelection)
        self.table_paiements.setAlternatingRowColors(True)
        layout.addWidget(self.table_paiements)
        
        # Boutons d'action
        actions = QHBoxLayout()
        
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.charger_eleve)
        actions.addWidget(btn_refresh)
        
        btn_imprimer = QPushButton("Ré-imprimer le reçu")
        btn_imprimer.clicked.connect(self.on_reimprimer)
        actions.addWidget(btn_imprimer)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(self.fermer_fiche.emit)
        actions.addWidget(btn_close)
        
        actions.addStretch()
        layout.addLayout(actions)
    
    def create_info_section(self):
        """
        Crée la section d'informations de l'élève.
        
        Returns:
            Layout de la section
        """
        layout = QVBoxLayout()
        
        # Nom et prénom
        self.lbl_nom = QLabel("Nom : ")
        self.lbl_nom.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_nom)
        
        # Classe et année
        self.lbl_classe = QLabel("Classe : ")
        layout.addWidget(self.lbl_classe)
        
        # Montant total dû
        self.lbl_total = QLabel("Total dû : ")
        layout.addWidget(self.lbl_total)
        
        # Solde
        self.lbl_solde = QLabel("Solde : ")
        self.lbl_solde.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_solde)
        
        # Statut
        self.lbl_statut = QLabel("Statut : ")
        self.lbl_statut.setStyleSheet("font-size: 14px; font-weight: 500;")
        layout.addWidget(self.lbl_statut)
        
        return layout
    
    def set_eleve(self, eleve_id):
        """
        Définit l'élève à afficher.
        
        Args:
            eleve_id: ID de l'élève
        """
        self.eleve_id = eleve_id
        self.charger_eleve()
    
    def charger_eleve(self):
        """Charge les informations de l'élève et ses paiements."""
        if not self.eleve_id:
            return
        
        try:
            # Charger les infos de l'élève
            eleve = EleveService.get_eleve_by_id(self.eleve_id)
            if not eleve:
                QMessageBox.critical(self, "Erreur", "Élève introuvable")
                return
            
            # Mettre à jour les labels
            self.lbl_nom.setText(f"Élève : {eleve['nom']} {eleve['prenom']}")
            self.lbl_classe.setText(f"Classe : {eleve['classe_nom']} - Année : {eleve['annee_libelle']}")
            self.lbl_total.setText(f"Total dû : {eleve['total_formate']}")
            self.lbl_solde.setText(f"Solde : {eleve['solde_formate']}")
            self.lbl_statut.setText(f"Statut : {eleve['statut']}")
            
            # Couleur du statut (texte coloré simple)
            if eleve['statut'] == STATUT_SOLDE:
                self.lbl_statut.setStyleSheet(
                    "font-size: 14px; font-weight: 500; color: #047857;"
                )
            elif eleve['statut'] == STATUT_PARTIEL:
                self.lbl_statut.setStyleSheet(
                    "font-size: 14px; font-weight: 500; color: #B45309;"
                )
            else:
                self.lbl_statut.setStyleSheet(
                    "font-size: 14px; font-weight: 500; color: #B91C1C;"
                )
            
            # Charger les paiements
            self.charger_paiements()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {e}")
    
    def charger_paiements(self):
        """Charge l'historique des paiements dans le tableau."""
        try:
            paiements = PaiementService.get_paiements_eleve(self.eleve_id)
            
            self.table_paiements.setRowCount(len(paiements))
            
            for row, paiement in enumerate(paiements):
                # Date
                self.table_paiements.setItem(row, 0, QTableWidgetItem(paiement['date_paiement']))
                
                # Montant
                self.table_paiements.setItem(row, 1, QTableWidgetItem(paiement['montant_formate']))
                
                # Mode
                self.table_paiements.setItem(row, 2, QTableWidgetItem(paiement['mode_texte']))
                
                # Numéro de reçu
                self.table_paiements.setItem(row, 3, QTableWidgetItem(paiement['numero_recu']))
                
                # Solde après
                self.table_paiements.setItem(row, 4, QTableWidgetItem(paiement['solde_formate']))
                
                # Stocker l'ID du paiement
                self.table_paiements.item(row, 0).setData(Qt.UserRole, paiement['id'])
            
            # Si aucun paiement
            if not paiements:
                self.table_paiements.setRowCount(1)
                self.table_paiements.setItem(0, 0, QTableWidgetItem("Aucun paiement enregistré"))
                self.table_paiements.setSpan(0, 0, 1, 5)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des paiements : {e}")
    
    def on_reimprimer(self):
        """Gère la ré-impression d'un reçu."""
        # Récupérer le paiement sélectionné
        current_row = self.table_paiements.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un paiement")
            return
        
        # Récupérer l'ID du paiement
        item = self.table_paiements.item(current_row, 0)
        if item:
            paiement_id = item.data(Qt.UserRole)
            if paiement_id:
                self.reimprimer_recu.emit(paiement_id)
            else:
                QMessageBox.information(self, "Information", "Aucun paiement à ré-imprimer")
