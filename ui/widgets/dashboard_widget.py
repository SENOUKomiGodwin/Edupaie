"""
Widget du tableau de bord.

Affiche les statistiques globales de l'application avec des cartes KPI
et un tableau de suivi des élèves par statut.
Utilise exclusivement les icônes Google Fonts (Material Icons), sans aucun emoji.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont
from services.dashboard_service import DashboardService
from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE
from ui import theme
from ui.icons import get_icon, creer_label_icone


class DashboardWidget(QWidget):
    """Widget du tableau de bord au design moderne avec icônes Google Fonts."""

    def __init__(self):
        super().__init__()
        self._current_annee_id = None
        self.setup_ui()
        self.charger_statistiques()

    def setup_ui(self):
        """Configure l'interface du tableau de bord."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # En-tête
        header = QHBoxLayout()
        header.setSpacing(0)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        breadcrumb = QLabel("Tableau de bord")
        breadcrumb.setObjectName("pageSubtitle")
        title_block.addWidget(breadcrumb)

        title = QLabel("Vue d'ensemble")
        title.setObjectName("pageTitle")
        title_block.addWidget(title)
        header.addLayout(title_block)

        header.addStretch()

        btn_refresh = QPushButton("  Actualiser")
        btn_refresh.setIcon(get_icon("refresh", theme.TEXTE_SECOND, 18))
        btn_refresh.setIconSize(QSize(18, 18))
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(36)
        btn_refresh.clicked.connect(self.charger_statistiques)
        header.addWidget(btn_refresh)

        layout.addLayout(header)

        # Grille de cartes KPI
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        # 1. Total élèves
        self.card_eleves = self._creer_carte_simple("Effectif total", "0 élève", "inscrits cette année")
        cards_row.addWidget(self.card_eleves['frame'])

        # 2. Total encaissé
        self.card_encaisse = self._creer_carte_kpi("Total encaissé", "0 FCFA", theme.TEXTE, "progressGreen", "check", theme.VERT)
        cards_row.addWidget(self.card_encaisse['frame'])

        # 3. Reste à payer
        self.card_restant = self._creer_carte_kpi("Reste à payer", "0 FCFA", theme.ORANGE, "progressOrange", "history", theme.ORANGE)
        cards_row.addWidget(self.card_restant['frame'])

        # 4. Non soldés
        self.card_non_soldes = self._creer_carte_simple("Élèves non soldés", "0", "nécessitent un suivi", theme.ROUGE)
        cards_row.addWidget(self.card_non_soldes['frame'])

        layout.addLayout(cards_row)

        # Section filtre et tableau
        table_card = QFrame()
        table_card.setObjectName("card")
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(16, 16, 16, 14)
        table_card_layout.setSpacing(12)

        # Barre supérieure du tableau : Titre + Filtre par statut
        filter_bar = QHBoxLayout()
        sub_title = QLabel("Répartition des élèves par statut")
        sub_title.setObjectName("sectionTitle")
        filter_bar.addWidget(sub_title)

        filter_bar.addStretch()

        filter_bar.addWidget(QLabel("Statut :"))

        self.statut_filter = QComboBox()
        self.statut_filter.addItem("Tous les statuts", None)
        self.statut_filter.addItem("Soldés", "soldé")
        self.statut_filter.addItem("Partiellement payés", "partiel")
        self.statut_filter.addItem("Non payés", "non_payé")
        self.statut_filter.setFixedWidth(180)
        self.statut_filter.currentIndexChanged.connect(self.filtrer_eleves)
        filter_bar.addWidget(self.statut_filter)

        table_card_layout.addLayout(filter_bar)

        # Tableau des élèves
        self.table_eleves = QTableWidget()
        self.table_eleves.setColumnCount(4)
        self.table_eleves.setHorizontalHeaderLabels([
            "Nom", "Prénom", "Classe", "Statut"
        ])
        self.table_eleves.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_eleves.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_eleves.setSelectionMode(QTableWidget.SingleSelection)
        self.table_eleves.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_eleves.verticalHeader().setVisible(False)
        self.table_eleves.setShowGrid(False)
        self.table_eleves.verticalHeader().setDefaultSectionSize(44)
        table_card_layout.addWidget(self.table_eleves, 1)

        layout.addWidget(table_card, 1)

    def _creer_carte_simple(self, label: str, val: str, sub: str, color: str = None) -> dict:
        """Crée une carte de compteur discret."""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(94)

        l = QVBoxLayout(frame)
        l.setContentsMargins(14, 12, 14, 12)
        l.setSpacing(3)

        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        l.addWidget(lbl)

        lbl_val = QLabel(val)
        lbl_val.setObjectName("statValue")
        if color:
            lbl_val.setStyleSheet(f"color: {color};")
        l.addWidget(lbl_val)

        lbl_sub = QLabel(sub)
        lbl_sub.setObjectName("legendLabel")
        l.addWidget(lbl_sub)

        l.addStretch()
        return {'frame': frame, 'lbl_value': lbl_val, 'lbl_sub': lbl_sub}

    def _creer_carte_kpi(self, label: str, val: str, val_color: str, progress_name: str, icon_name: str, icon_col: str) -> dict:
        """Crée une carte avec icône Google Fonts et barre de progression."""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(94)

        l = QVBoxLayout(frame)
        l.setContentsMargins(14, 12, 14, 12)
        l.setSpacing(3)

        top_row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        top_row.addWidget(lbl)
        top_row.addStretch()

        icon = creer_label_icone(icon_name, icon_col, 16)
        top_row.addWidget(icon)
        l.addLayout(top_row)

        lbl_val = QLabel(val)
        lbl_val.setObjectName("statValue")
        lbl_val.setStyleSheet(f"color: {val_color};")
        l.addWidget(lbl_val)

        l.addStretch()

        p = QProgressBar()
        p.setObjectName(progress_name)
        p.setTextVisible(False)
        p.setRange(0, 100)
        p.setValue(0)
        l.addWidget(p)

        return {'frame': frame, 'lbl_value': lbl_val, 'progress': p}

    def charger_statistiques(self, annee_id: int = None):
        """
        Charge et affiche les statistiques globales.
        
        Args:
            annee_id: Optionnel, filtre par année scolaire
        """
        self._current_annee_id = annee_id
        try:
            stats = DashboardService.get_statistiques(annee_id)

            nb_eleves = stats.get('nb_eleves', 0)
            self.card_eleves['lbl_value'].setText(f"{nb_eleves} élève{'s' if nb_eleves > 1 else ''}")
            self.card_encaisse['lbl_value'].setText(stats.get('total_encaisse_formate', '0 FCFA'))
            self.card_restant['lbl_value'].setText(stats.get('total_restant_formate', '0 FCFA'))
            self.card_non_soldes['lbl_value'].setText(str(stats.get('nb_non_soldes', 0)))

            encaisse = stats.get('total_encaisse', 0)
            restant = stats.get('total_restant', 0)
            total = encaisse + restant
            if total > 0:
                self.card_encaisse['progress'].setValue(int((encaisse / total) * 100))
                self.card_restant['progress'].setValue(int((restant / total) * 100))

            self.filtrer_eleves()

        except Exception as e:
            print(f"Erreur lors du chargement des statistiques : {e}")

    def filtrer_eleves(self):
        """Filtre les élèves du tableau par statut."""
        statut = self.statut_filter.currentData()

        try:
            eleves = DashboardService.get_eleves_par_statut(statut, self._current_annee_id)
            self.table_eleves.setRowCount(len(eleves))

            for row, eleve in enumerate(eleves):
                item_nom = QTableWidgetItem(eleve['nom'])
                item_nom.setFont(QFont("Segoe UI", 10, QFont.Medium))
                self.table_eleves.setItem(row, 0, item_nom)

                self.table_eleves.setItem(row, 1, QTableWidgetItem(eleve['prenom']))
                self.table_eleves.setItem(row, 2, QTableWidgetItem(eleve['classe_nom']))

                st = eleve['statut']
                statut_item = QTableWidgetItem(st)
                statut_item.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
                if st == STATUT_SOLDE:
                    statut_item.setForeground(QColor(theme.VERT))
                elif st == STATUT_PARTIEL:
                    statut_item.setForeground(QColor(theme.ORANGE))
                else:
                    statut_item.setForeground(QColor(theme.ROUGE))
                self.table_eleves.setItem(row, 3, statut_item)

            if not eleves:
                self.table_eleves.setRowCount(1)
                empty_item = QTableWidgetItem("Aucun élève trouvé pour ce statut")
                empty_item.setTextAlignment(Qt.AlignCenter)
                self.table_eleves.setItem(0, 0, empty_item)
                self.table_eleves.setSpan(0, 0, 1, 4)

        except Exception as e:
            print(f"Erreur lors du filtrage des élèves : {e}")
