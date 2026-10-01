"""
Widget de liste des élèves.

Affiche la liste des élèves avec recherche, filtres et actions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QTableView, QMessageBox, QFrame, QLabel
)
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel
from PySide6.QtWidgets import QHeaderView, QStyledItemDelegate, QStyle
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics
from ui.models.eleve_table_model import EleveTableModel
from services.eleve_service import EleveService
from services.classe_service import ClasseService
import logging


class EleveDelegate(QStyledItemDelegate):
    """Delegate personnalisé pour la colonne Élève avec pastille d'initiales grise."""

    def paint(self, painter, option, index):
        """Dessine la cellule avec pastille d'initiales grise et nom complet."""
        try:
            painter.save()

            # Récupérer les données
            model = index.model()
            text = model.data(index, Qt.DisplayRole)

            if not text:
                return

            # Extraire les initiales
            parts = text.split()
            if len(parts) >= 2:
                initials = parts[0][0].upper() + parts[1][0].upper()
            elif len(parts) == 1:
                initials = parts[0][0].upper() + parts[0][0].upper()
            else:
                initials = "??"

            # Dessiner le fond si sélectionné
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, QColor(236, 253, 245))  # #ECFDF5
            else:
                painter.fillRect(option.rect, QColor(255, 255, 255))  # Blanc

            # Configuration du cercle
            circle_size = 32
            circle_x = option.rect.left() + 10
            circle_y = option.rect.top() + (option.rect.height() - circle_size) // 2

            # Dessiner le cercle gris neutre
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(240, 238, 236))  # #F0EEEC
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)

            # Dessiner les initiales
            painter.setPen(QColor(75, 85, 99))  # Gris foncé pour le texte
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)

            # Centrer les initiales dans le cercle
            fm = QFontMetrics(font)
            rect_initials = fm.boundingRect(initials)
            initials_x = circle_x + (circle_size - rect_initials.width()) // 2
            initials_y = circle_y + (circle_size + rect_initials.height()) // 2 - 2
            painter.drawText(initials_x, initials_y, initials)

            # Dessiner le nom complet à droite du cercle
            text_x = circle_x + circle_size + 12
            font_normal = QFont()
            font_normal.setPointSize(10)
            fm_normal = QFontMetrics(font_normal)
            text_y = option.rect.top() + (option.rect.height() + fm_normal.height()) // 2 - 2
            painter.setPen(QColor(31, 41, 55))  # Gris très foncé
            painter.setFont(font_normal)
            painter.drawText(text_x, text_y, text)

        except Exception as e:
            logging.exception("Erreur dans EleveDelegate.paint()")
            super().paint(painter, option, index)
        finally:
            painter.restore()


class EleveListWidget(QWidget):
    """Widget de liste des élèves."""

    # Signaux
    nouveau_eleve = Signal()
    modifier_eleve = Signal(int)  # ID de l'élève
    supprimer_eleve = Signal(int)  # ID de l'élève
    enregistrer_paiement = Signal(int)  # ID de l'élève
    voir_fiche = Signal(int)  # ID de l'élève

    def __init__(self):
        super().__init__()
        self.model = EleveTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        """Configure l'interface de la liste."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Carte englobante
        carte = QFrame()
        carte.setObjectName("card")
        carte_layout = QVBoxLayout(carte)
        carte_layout.setContentsMargins(16, 14, 16, 14)
        carte_layout.setSpacing(12)

        # Barre d'outils
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un élève (nom, prénom)...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(320)
        self.search_input.textChanged.connect(self.filtrer_eleves)
        toolbar.addWidget(self.search_input)

        # Filtre par classe
        self.classe_filter = QComboBox()
        self.classe_filter.addItem("Toutes les classes", None)
        self.classe_filter.setFixedWidth(180)
        self.charger_classes()
        self.classe_filter.currentIndexChanged.connect(self.filtrer_eleves)
        toolbar.addWidget(self.classe_filter)

        toolbar.addStretch()

        # Compteur d'élèves avec pagination
        self.lbl_compteur = QLabel("0 élève")
        self.lbl_compteur.setObjectName("pageSubtitle")
        toolbar.addWidget(self.lbl_compteur)

        # Bouton nouvel élève (action principale)
        btn_new = QPushButton("Nouvel élève")
        btn_new.setProperty("variant", "primary")
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.clicked.connect(self.nouveau_eleve.emit)
        toolbar.addWidget(btn_new)

        carte_layout.addLayout(toolbar)

        # Tableau
        self.table = QTableView()
        self.table.setModel(self.proxy_model)
        self.table.setItemDelegateForColumn(0, EleveDelegate())
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.on_double_click)

        # Styling CSS
        self.table.setStyleSheet("""
            QTableView {
                border: none;
                background-color: white;
                selection-background-color: #ECFDF5;
                selection-color: black;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #E5E7EB;
                min-height: 44px;
            }
            QTableView::item:selected {
                background-color: #ECFDF5;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                font-size: 11px;
                font-weight: 500;
                color: #374151;
            }
        """)

        # Configurer le tri sur le proxy model
        self.proxy_model.setSortRole(Qt.DisplayRole)
        self.table.horizontalHeader().setSectionsMovable(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        carte_layout.addWidget(self.table, 1)

        # Barre d'actions
        actions = QHBoxLayout()
        actions.setSpacing(10)

        btn_view = QPushButton("Voir fiche")
        btn_view.clicked.connect(self.on_voir_fiche)
        actions.addWidget(btn_view)

        btn_edit = QPushButton("Modifier")
        btn_edit.clicked.connect(self.on_modifier)
        actions.addWidget(btn_edit)

        btn_pay = QPushButton("Enregistrer paiement")
        btn_pay.setProperty("variant", "primary")
        btn_pay.clicked.connect(self.on_paiement)
        actions.addWidget(btn_pay)

        btn_delete = QPushButton("Supprimer")
        btn_delete.setProperty("variant", "danger")
        btn_delete.clicked.connect(self.on_supprimer)
        actions.addWidget(btn_delete)

        actions.addStretch()
        carte_layout.addLayout(actions)

        layout.addWidget(carte)

    def charger_classes(self):
        """Charge les classes dans le filtre."""
        try:
            classes = ClasseService.get_all_classes()
            for classe in classes:
                self.classe_filter.addItem(classe['nom'], classe['id'])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des classes : {e}")

    def charger_donnees(self):
        """Charge les données des élèves."""
        try:
            eleves = EleveService.get_all_eleves()
            self.model.set_data(eleves)
            self.mettre_a_jour_compteur(len(eleves))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des élèves : {e}")

    def filtrer_eleves(self):
        """Filtre les élèves selon la recherche et la classe."""
        texte = self.search_input.text().strip()
        classe_id = self.classe_filter.currentData()

        try:
            if texte or classe_id:
                eleves = EleveService.rechercher_eleves(texte, classe_id)
            else:
                eleves = EleveService.get_all_eleves()
            self.model.set_data(eleves)
            self.mettre_a_jour_compteur(len(eleves))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {e}")

    def mettre_a_jour_compteur(self, nb: int):
        """
        Met à jour le compteur d'élèves affiché.

        Args:
            nb: Nombre d'élèves affichés
        """
        if nb == 0:
            self.lbl_compteur.setText("0 élève")
        else:
            self.lbl_compteur.setText(f"{nb} élève{'s' if nb > 1 else ''}")

    def eleve_selectionne_id(self) -> int | None:
        """
        Récupère l'ID de l'élève sélectionné.

        Returns:
            ID de l'élève ou None si aucune sélection
        """
        index = self.table.currentIndex()
        if not index.isValid():
            return None
        # Convertir l'index du proxy model en index du modèle source
        source_index = self.proxy_model.mapToSource(index)
        return self.model.get_eleve_id(source_index.row())

    def on_double_click(self, index):
        """Gère le double-clic sur une ligne (ouvre la fiche)."""
        source_index = self.proxy_model.mapToSource(index)
        eleve_id = self.model.get_eleve_id(source_index.row())
        if eleve_id:
            self.voir_fiche.emit(eleve_id)

    def on_modifier(self):
        """Gère le clic sur le bouton Modifier."""
        eleve_id = self.eleve_selectionne_id()
        if eleve_id:
            self.modifier_eleve.emit(eleve_id)
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")

    def on_supprimer(self):
        """Gère le clic sur le bouton Supprimer."""
        eleve_id = self.eleve_selectionne_id()
        if not eleve_id:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")
            return

        # Récupérer les infos de l'élève
        from services.eleve_service import EleveService
        try:
            eleve = EleveService.get_eleve_by_id(eleve_id)
            if not eleve:
                QMessageBox.critical(self, "Erreur", "Élève introuvable")
                return

            # Vérifier si l'élève a des paiements
            from services.paiement_service import PaiementService
            paiements = PaiementService.get_paiements_eleve(eleve_id)
            nb_paiements = len(paiements)

            if nb_paiements > 0:
                # Règle : interdire la suppression si des paiements existent
                QMessageBox.warning(
                    self,
                    "Suppression impossible",
                    f"Impossible de supprimer {eleve['prenom']} {eleve['nom']} car il a {nb_paiements} paiement(s) enregistré(s).\n\n"
                    f"Pour supprimer cet élève, vous devez d'abord supprimer ses paiements."
                )
                return

            # Confirmation
            reponse = QMessageBox.question(
                self,
                "Confirmation de suppression",
                f"Êtes-vous sûr de vouloir supprimer {eleve['prenom']} {eleve['nom']} ({eleve['classe_nom']}) ?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reponse == QMessageBox.Yes:
                try:
                    EleveService.supprimer_eleve(eleve_id)
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"{eleve['prenom']} {eleve['nom']} a été supprimé avec succès."
                    )
                    self.rafraichir()
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {e}")

    def on_paiement(self):
        """Gère le clic sur le bouton Enregistrer paiement."""
        eleve_id = self.eleve_selectionne_id()
        if eleve_id:
            self.enregistrer_paiement.emit(eleve_id)
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")

    def on_voir_fiche(self):
        """Gère le clic sur le bouton Voir fiche."""
        eleve_id = self.eleve_selectionne_id()
        if eleve_id:
            self.voir_fiche.emit(eleve_id)
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")

    def rafraichir(self):
        """Rafraîchit la liste des élèves."""
        self.charger_donnees()
