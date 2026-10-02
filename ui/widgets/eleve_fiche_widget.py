"""
Widget de fiche élève.

Affiche les informations d'un élève, son solde, son statut et l'historique complet
de ses paiements dans une interface organisée par cartes élégantes.
Utilise exclusivement les icônes Google Fonts (Material Icons), sans aucun emoji.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QFont
from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE
from ui import theme
from ui.icons import get_icon


class EleveFicheWidget(QWidget):
    """Widget de fiche élève stylisé avec icônes Google Fonts."""

    # Signaux
    reimprimer_recu = Signal(int)
    fermer_fiche = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.eleve_id = None
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface de la fiche élève."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # En-tête : Breadcrumb + Titre + Bouton Retour
        header = QHBoxLayout()
        header.setSpacing(0)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        breadcrumb = QLabel("Élèves  ›  Fiche détaillée")
        breadcrumb.setObjectName("pageSubtitle")
        title_block.addWidget(breadcrumb)

        self.title_nom = QLabel("Fiche élève")
        self.title_nom.setObjectName("pageTitle")
        title_block.addWidget(self.title_nom)
        header.addLayout(title_block)

        header.addStretch()

        btn_retour = QPushButton("  Retour à la liste")
        btn_retour.setIcon(get_icon("arrow_back", theme.TEXTE_SECOND, 18))
        btn_retour.setIconSize(QSize(18, 18))
        btn_retour.setCursor(Qt.PointingHandCursor)
        btn_retour.setFixedHeight(38)
        btn_retour.clicked.connect(self.fermer_fiche.emit)
        header.addWidget(btn_retour)

        layout.addLayout(header)

        # Carte d'identité et état financier de l'élève
        info_card = QFrame()
        info_card.setObjectName("card")
        info_card_layout = QHBoxLayout(info_card)
        info_card_layout.setContentsMargins(20, 18, 20, 18)
        info_card_layout.setSpacing(20)

        # Avatar grand format
        self.avatar_label = QLabel("??")
        self.avatar_label.setFixedSize(54, 54)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            background-color: #F0EEEC;
            color: #4B5563;
            border-radius: 27px;
            font-size: 18px;
            font-weight: 700;
        """)
        info_card_layout.addWidget(self.avatar_label)

        # Identité
        id_layout = QVBoxLayout()
        id_layout.setSpacing(4)
        self.lbl_nom_complet = QLabel("Nom de l'élève")
        self.lbl_nom_complet.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {theme.TEXTE};")
        id_layout.addWidget(self.lbl_nom_complet)

        self.lbl_classe_annee = QLabel("Classe : - | Année : -")
        self.lbl_classe_annee.setObjectName("pageSubtitle")
        id_layout.addWidget(self.lbl_classe_annee)
        info_card_layout.addLayout(id_layout)

        info_card_layout.addStretch()

        # Bloc financier : Total dû, Solde restant, Statut
        finance_row = QHBoxLayout()
        finance_row.setSpacing(16)

        # Total dû
        c_total = self._creer_mini_bloc("Total dû", "--", theme.TEXTE)
        self.lbl_total_du = c_total['val']
        finance_row.addWidget(c_total['frame'])

        # Solde restant
        c_solde = self._creer_mini_bloc("Solde restant", "--", theme.ORANGE)
        self.lbl_solde_restant = c_solde['val']
        finance_row.addWidget(c_solde['frame'])

        # Statut
        c_statut = self._creer_mini_bloc("Statut", "--", theme.VERT)
        self.lbl_statut = c_statut['val']
        finance_row.addWidget(c_statut['frame'])

        info_card_layout.addLayout(finance_row)
        layout.addWidget(info_card)

        # Carte Historique des paiements
        hist_card = QFrame()
        hist_card.setObjectName("card")
        hist_card_layout = QVBoxLayout(hist_card)
        hist_card_layout.setContentsMargins(18, 16, 18, 16)
        hist_card_layout.setSpacing(12)

        # Titre de la section
        hist_header = QHBoxLayout()
        hist_title = QLabel("Historique des paiements enregistrés")
        hist_title.setObjectName("sectionTitle")
        hist_header.addWidget(hist_title)
        hist_header.addStretch()

        btn_refresh = QPushButton("  Actualiser")
        btn_refresh.setIcon(get_icon("refresh", theme.TEXTE_SECOND, 16))
        btn_refresh.setIconSize(QSize(16, 16))
        btn_refresh.setFixedHeight(34)
        btn_refresh.clicked.connect(self.charger_eleve)
        hist_header.addWidget(btn_refresh)

        btn_imprimer = QPushButton("  Ré-imprimer le reçu")
        btn_imprimer.setProperty("variant", "primary")
        btn_imprimer.setIcon(get_icon("print", "#FFFFFF", 16))
        btn_imprimer.setIconSize(QSize(16, 16))
        btn_imprimer.setFixedHeight(34)
        btn_imprimer.clicked.connect(self.on_reimprimer)
        hist_header.addWidget(btn_imprimer)

        hist_card_layout.addLayout(hist_header)

        # Tableau des paiements
        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(5)
        self.table_paiements.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "N° Reçu", "Solde après"
        ])
        self.table_paiements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_paiements.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_paiements.setSelectionMode(QTableWidget.SingleSelection)
        self.table_paiements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_paiements.verticalHeader().setVisible(False)
        self.table_paiements.setShowGrid(False)
        self.table_paiements.verticalHeader().setDefaultSectionSize(46)
        hist_card_layout.addWidget(self.table_paiements, 1)

        layout.addWidget(hist_card, 1)

    def _creer_mini_bloc(self, label: str, val: str, val_col: str) -> dict:
        """Crée un petit bloc statistique encadré."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {theme.FOND};
            border: 1px solid {theme.BORDURE};
            border-radius: 8px;
        """)
        frame.setFixedSize(140, 60)
        l = QVBoxLayout(frame)
        l.setContentsMargins(10, 8, 10, 8)
        l.setSpacing(2)

        lbl = QLabel(label)
        lbl.setObjectName("legendLabel")
        l.addWidget(lbl)

        val_lbl = QLabel(val)
        val_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {val_col};")
        l.addWidget(val_lbl)

        return {'frame': frame, 'val': val_lbl}

    def set_eleve(self, eleve_id: int):
        """Définit l'élève à afficher."""
        self.eleve_id = eleve_id
        self.charger_eleve()

    def charger_eleve(self):
        """Charge les informations et les paiements de l'élève."""
        if not self.eleve_id:
            return

        try:
            eleve = EleveService.get_eleve_by_id(self.eleve_id)
            if not eleve:
                QMessageBox.critical(self, "Erreur", "Élève introuvable")
                return

            prenom = eleve.get('prenom', '')
            nom = eleve.get('nom', '')
            self.title_nom.setText(f"{prenom} {nom}")
            self.lbl_nom_complet.setText(f"{prenom} {nom}")
            self.lbl_classe_annee.setText(f"Classe : {eleve.get('classe_nom', '-')}   |   Année scolaire : {eleve.get('annee_libelle', '-')}")

            # Initiales de l'avatar
            initials = (prenom[0].upper() if prenom else "") + (nom[0].upper() if nom else "")
            self.avatar_label.setText(initials or "??")

            # Données financières
            self.lbl_total_du.setText(eleve.get('total_formate', '0 FCFA'))
            self.lbl_solde_restant.setText(eleve.get('solde_formate', '0 FCFA'))

            statut = eleve.get('statut', '')
            self.lbl_statut.setText(statut)
            if statut == STATUT_SOLDE:
                self.lbl_statut.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {theme.VERT};")
            elif statut == STATUT_PARTIEL:
                self.lbl_statut.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {theme.ORANGE};")
            else:
                self.lbl_statut.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {theme.ROUGE};")

            self.charger_paiements()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement : {e}")

    def charger_paiements(self):
        """Charge l'historique des règlements de l'élève."""
        try:
            paiements = PaiementService.get_paiements_eleve(self.eleve_id)
            self.table_paiements.setRowCount(len(paiements))

            for row, p in enumerate(paiements):
                self.table_paiements.setItem(row, 0, QTableWidgetItem(p['date_paiement']))

                item_montant = QTableWidgetItem(p['montant_formate'])
                item_montant.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
                self.table_paiements.setItem(row, 1, item_montant)

                self.table_paiements.setItem(row, 2, QTableWidgetItem(p['mode_texte']))
                self.table_paiements.setItem(row, 3, QTableWidgetItem(p['numero_recu']))
                self.table_paiements.setItem(row, 4, QTableWidgetItem(p['solde_formate']))

                self.table_paiements.item(row, 0).setData(Qt.UserRole, p['id'])

            if not paiements:
                self.table_paiements.setRowCount(1)
                empty = QTableWidgetItem("Aucun paiement enregistré pour le moment")
                empty.setTextAlignment(Qt.AlignCenter)
                self.table_paiements.setItem(0, 0, empty)
                self.table_paiements.setSpan(0, 0, 1, 5)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des paiements : {e}")

    def on_reimprimer(self):
        """Déclenche la ré-impression du reçu pour le paiement sélectionné."""
        current_row = self.table_paiements.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un paiement dans la liste")
            return

        item = self.table_paiements.item(current_row, 0)
        if item:
            paiement_id = item.data(Qt.UserRole)
            if paiement_id:
                self.reimprimer_recu.emit(paiement_id)
            else:
                QMessageBox.information(self, "Information", "Aucun paiement sélectionné")
