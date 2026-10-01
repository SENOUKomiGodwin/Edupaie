"""
Widget du tableau de bord.

Affiche les statistiques globales de l'application.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.dashboard_service import DashboardService
from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE


class DashboardWidget(QWidget):
    """Widget du tableau de bord."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.charger_statistiques()
    
    def setup_ui(self):
        """Configure l'interface du tableau de bord."""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Tableau de bord")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Grille de statistiques
        stats_layout = QGridLayout()
        
        # Carte: Nombre d'élèves
        self.lbl_nb_eleves = QLabel("0")
        self.lbl_nb_eleves.setStyleSheet("""
            font-size: 32px; font-weight: bold; color: #1976D2;
            background-color: #E3F2FD; padding: 20px; border-radius: 10px;
        """)
        self.lbl_nb_eleves.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(QLabel("Nombre d'élèves"), 0, 0)
        stats_layout.addWidget(self.lbl_nb_eleves, 1, 0)
        
        # Carte: Total encaissé
        self.lbl_total_encaisse = QLabel("0 FCFA")
        self.lbl_total_encaisse.setStyleSheet("""
            font-size: 24px; font-weight: bold; color: #388E3C;
            background-color: #E8F5E9; padding: 20px; border-radius: 10px;
        """)
        self.lbl_total_encaisse.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(QLabel("Total encaissé"), 0, 1)
        stats_layout.addWidget(self.lbl_total_encaisse, 1, 1)
        
        # Carte: Total restant dû
        self.lbl_total_restant = QLabel("0 FCFA")
        self.lbl_total_restant.setStyleSheet("""
            font-size: 24px; font-weight: bold; color: #D32F2F;
            background-color: #FFEBEE; padding: 20px; border-radius: 10px;
        """)
        self.lbl_total_restant.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(QLabel("Total restant dû"), 0, 2)
        stats_layout.addWidget(self.lbl_total_restant, 1, 2)
        
        # Carte: Élèves non soldés
        self.lbl_nb_non_soldes = QLabel("0")
        self.lbl_nb_non_soldes.setStyleSheet("""
            font-size: 32px; font-weight: bold; color: #F57C00;
            background-color: #FFF3E0; padding: 20px; border-radius: 10px;
        """)
        self.lbl_nb_non_soldes.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(QLabel("Élèves non soldés"), 0, 3)
        stats_layout.addWidget(self.lbl_nb_non_soldes, 1, 3)
        
        layout.addLayout(stats_layout)
        
        layout.addSpacing(20)
        
        # Section liste des élèves par statut
        list_layout = QHBoxLayout()
        
        list_layout.addWidget(QLabel("Filtrer par statut :"))
        
        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Tous", None)
        self.statut_filter.addItem("Soldés", "soldé")
        self.statut_filter.addItem("Partiellement payés", "partiel")
        self.statut_filter.addItem("Non payés", "non_payé")
        self.statut_filter.currentIndexChanged.connect(self.filtrer_eleves)
        list_layout.addWidget(self.statut_filter)
        
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.clicked.connect(self.charger_statistiques)
        list_layout.addWidget(btn_refresh)
        
        list_layout.addStretch()
        layout.addLayout(list_layout)
        
        # Tableau des élèves
        self.table_eleves = QTableWidget()
        self.table_eleves.setColumnCount(4)
        self.table_eleves.setHorizontalHeaderLabels([
            "Nom", "Prénom", "Classe", "Statut"
        ])
        self.table_eleves.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_eleves.setAlternatingRowColors(True)
        layout.addWidget(self.table_eleves)
    
    def charger_statistiques(self):
        """Charge et affiche les statistiques."""
        try:
            stats = DashboardService.get_statistiques()
            
            # Mettre à jour les labels
            self.lbl_nb_eleves.setText(str(stats['nb_eleves']))
            self.lbl_total_encaisse.setText(stats['total_encaisse_formate'])
            self.lbl_total_restant.setText(stats['total_restant_formate'])
            self.lbl_nb_non_soldes.setText(str(stats['nb_non_soldes']))
            
            # Charger la liste des élèves
            self.filtrer_eleves()
            
        except Exception as e:
            print(f"Erreur lors du chargement des statistiques : {e}")
    
    def filtrer_eleves(self):
        """Filtre et affiche les élèves selon le statut."""
        statut = self.statut_filter.currentData()
        
        try:
            eleves = DashboardService.get_eleves_par_statut(statut)
            
            self.table_eleves.setRowCount(len(eleves))
            
            for row, eleve in enumerate(eleves):
                self.table_eleves.setItem(row, 0, QTableWidgetItem(eleve['nom']))
                self.table_eleves.setItem(row, 1, QTableWidgetItem(eleve['prenom']))
                self.table_eleves.setItem(row, 2, QTableWidgetItem(eleve['classe_nom']))

                # Statut en texte coloré
                statut_item = QTableWidgetItem(eleve['statut'])
                statut = eleve['statut']
                if statut == STATUT_SOLDE:
                    statut_item.setForeground(QColor(4, 120, 87))  # #047857
                elif statut == STATUT_PARTIEL:
                    statut_item.setForeground(QColor(180, 83, 9))  # #B45309
                elif statut == STATUT_NON_PAYE:
                    statut_item.setForeground(QColor(185, 28, 28))  # #B91C1C
                self.table_eleves.setItem(row, 3, statut_item)
            
            if not eleves:
                self.table_eleves.setRowCount(1)
                self.table_eleves.setItem(0, 0, QTableWidgetItem("Aucun élève"))
                self.table_eleves.setSpan(0, 0, 1, 4)
                
        except Exception as e:
            print(f"Erreur lors du filtrage des élèves : {e}")
