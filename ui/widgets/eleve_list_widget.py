"""
Widget de liste des élèves.

Affiche la liste des élèves avec cartes résumé KPI, barre de filtres à chips,
tableau épuré avec avatars d'initiales, et barre d'actions contextuelle.
Utilise exclusivement les icônes Google Fonts (Material Icons), sans aucun emoji.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QTableView, QMessageBox, QFrame, QLabel,
    QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QSize
from PySide6.QtWidgets import QHeaderView, QStyledItemDelegate, QStyle
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics
from ui.models.eleve_table_model import EleveTableModel
from services.eleve_service import EleveService
from services.classe_service import ClasseService
from ui import theme
from ui.icons import get_icon, creer_label_icone
import logging


class EleveDelegate(QStyledItemDelegate):
    """Delegate personnalisé pour la colonne Élève avec pastille d'initiales grise."""

    def paint(self, painter, option, index):
        """Dessine la cellule avec pastille d'initiales grise et nom complet (élué si trop long)."""
        try:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)

            # Récupérer les données
            model = index.model()
            text = model.data(index, Qt.DisplayRole) or ""
            full_text = model.data(index, Qt.UserRole) or text  # Nom complet pour tooltip

            # Extraire les initiales
            parts = text.split()
            if len(parts) >= 2:
                initials = parts[0][0].upper() + parts[1][0].upper()
            elif len(parts) == 1 and parts[0]:
                initials = parts[0][:2].upper()
            else:
                initials = "??"

            # Dessiner le fond si sélectionné ou normal
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, QColor(theme.VERT_FOND))
            else:
                painter.fillRect(option.rect, QColor(theme.CARTE))

            # Configuration du cercle avatar
            circle_size = 32
            circle_x = option.rect.left() + 14  # Padding gauche
            circle_y = option.rect.top() + (option.rect.height() - circle_size) // 2

            # Cercle gris doux
            painter.setBrush(QColor("#F0EEEC"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(circle_x, circle_y, circle_size, circle_size)

            # Initiales dans le cercle
            painter.setPen(QColor(theme.TEXTE_SECOND))
            font_initials = QFont("Segoe UI", 9)
            font_initials.setWeight(QFont.DemiBold)
            painter.setFont(font_initials)

            fm = QFontMetrics(font_initials)
            rect_initials = fm.boundingRect(initials)
            ix = circle_x + (circle_size - rect_initials.width()) // 2
            iy = circle_y + (circle_size + fm.ascent() - fm.descent()) // 2
            painter.drawText(ix, iy, initials)

            # Nom complet à droite de l'avatar (élué si trop long)
            text_x = circle_x + circle_size + 12
            available_width = option.rect.right() - text_x - 14  # Marge à droite
            
            font_name = QFont("Segoe UI", 10)
            font_name.setWeight(QFont.Medium)
            painter.setFont(font_name)
            painter.setPen(QColor(theme.TEXTE))
            fm_name = QFontMetrics(font_name)
            
            # Éluder le texte si trop long
            elided_text = fm_name.elidedText(text, Qt.ElideRight, available_width)
            
            text_y = option.rect.top() + (option.rect.height() + fm_name.ascent() - fm_name.descent()) // 2
            painter.drawText(text_x, text_y, elided_text)

        except Exception as e:
            logging.exception("Erreur dans EleveDelegate.paint()")
            super().paint(painter, option, index)
        finally:
            painter.restore()


class EleveListWidget(QWidget):
    """Widget de liste des élèves avec design épuré et icônes Google Fonts."""

    # Signaux
    nouveau_eleve = Signal()
    modifier_eleve = Signal(int)
    supprimer_eleve = Signal(int)
    enregistrer_paiement = Signal(int)
    voir_fiche = Signal(int)

    def __init__(self):
        super().__init__()
        self.model = EleveTableModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self._current_filter = "tous"
        self._current_annee_id = None
        self._all_eleves = []
        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        """Configure l'interface complète de la liste."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # ===== 1. En-tête : Breadcrumb + Titre + Bouton Nouvel élève =====
        header = QHBoxLayout()
        header.setSpacing(0)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)
        breadcrumb = QLabel("Élèves")
        breadcrumb.setObjectName("pageSubtitle")
        title_block.addWidget(breadcrumb)

        title = QLabel("Liste des élèves")
        title.setObjectName("pageTitle")
        title_block.addWidget(title)
        header.addLayout(title_block)

        header.addStretch()

        btn_new = QPushButton("  Nouvel élève")
        btn_new.setObjectName("btnNouvelEleve")
        btn_new.setProperty("variant", "primary")
        btn_new.setIcon(get_icon("add", "#FFFFFF", 18))
        btn_new.setIconSize(QSize(18, 18))
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.setFixedHeight(38)
        btn_new.clicked.connect(self.nouveau_eleve.emit)
        header.addWidget(btn_new)

        layout.addLayout(header)

        # ===== 2. Cartes résumé KPI =====
        self._create_stat_cards(layout)

        # ===== 3. Barre de filtres (Recherche, Classe, Chips) =====
        self._create_filter_bar(layout)

        # ===== 4. Tableau dans une carte blanche =====
        table_card = QFrame()
        table_card.setObjectName("card")
        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(0, 0, 0, 0)
        table_card_layout.setSpacing(0)

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
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # Hauteur des lignes
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Tailles des colonnes
        self.proxy_model.setSortRole(Qt.DisplayRole)
        self.table.horizontalHeader().setSectionsMovable(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Alignement des en-têtes
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Aligner spécifiquement les colonnes numériques à droite
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        table_card_layout.addWidget(self.table, 1)

        # Ligne de séparation
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {theme.BORDURE}; max-height: 1px; border: none;")
        table_card_layout.addWidget(sep)

        # Footer du tableau avec pagination
        table_footer = QHBoxLayout()
        table_footer.setContentsMargins(16, 10, 16, 10)

        self.lbl_pagination = QLabel("1 à 0 sur 0 élèves")
        self.lbl_pagination.setObjectName("legendLabel")
        table_footer.addWidget(self.lbl_pagination)

        table_footer.addStretch()

        pagination_controls = QLabel("‹  1  2  3  ›")
        pagination_controls.setStyleSheet(f"color: {theme.TEXTE_SECOND}; font-weight: 500; font-size: 12px;")
        table_footer.addWidget(pagination_controls)

        table_card_layout.addLayout(table_footer)
        layout.addWidget(table_card, 1)

        # ===== 5. Barre d'actions contextuelle en bas =====
        self._create_action_bar(layout)

    def _create_stat_cards(self, parent_layout):
        """Crée les 3 cartes de statistiques KPI avec icônes Google Fonts."""
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        # 1. Carte Encaissé
        self.card_encaisse = self._make_stat_card(
            label="Encaissé",
            icon_name="check",
            icon_color=theme.VERT,
            val_color=theme.TEXTE,
            progress_name="progressGreen"
        )
        cards_row.addWidget(self.card_encaisse['frame'])

        # 2. Carte Reste à payer
        self.card_reste = self._make_stat_card(
            label="Reste à payer",
            icon_name="history",
            icon_color=theme.ORANGE,
            val_color=theme.ORANGE,
            progress_name="progressOrange"
        )
        cards_row.addWidget(self.card_reste['frame'])

        # 3. Carte Non soldés
        self.card_non_soldes = self._make_count_card(
            label="Non soldés",
            icon_name="warning",
            icon_color=theme.ROUGE
        )
        cards_row.addWidget(self.card_non_soldes['frame'])

        parent_layout.addLayout(cards_row)

    def _make_stat_card(self, label: str, icon_name: str, icon_color: str, val_color: str, progress_name: str) -> dict:
        """Crée une carte de statistique avec icône Google Fonts et barre de progression."""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(94)

        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(4)

        # Ligne supérieure : Label + Icône Google Fonts
        top_row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        top_row.addWidget(lbl)
        top_row.addStretch()

        icon_badge = creer_label_icone(icon_name, icon_color, 16)
        top_row.addWidget(icon_badge)
        card_layout.addLayout(top_row)

        # Valeur principale
        lbl_value = QLabel("0 FCFA")
        lbl_value.setObjectName("statValue")
        lbl_value.setStyleSheet(f"color: {val_color};")
        card_layout.addWidget(lbl_value)

        card_layout.addStretch()

        # Barre de progression
        progress = QProgressBar()
        progress.setObjectName(progress_name)
        progress.setTextVisible(False)
        progress.setRange(0, 100)
        progress.setValue(0)
        card_layout.addWidget(progress)

        return {'frame': frame, 'lbl_value': lbl_value, 'progress': progress}

    def _make_count_card(self, label: str, icon_name: str, icon_color: str) -> dict:
        """Crée la carte de comptage avec icône Google Fonts."""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setFixedHeight(94)

        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(3)

        # Ligne supérieure
        top_row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        top_row.addWidget(lbl)
        top_row.addStretch()

        icon_badge = creer_label_icone(icon_name, icon_color, 16)
        top_row.addWidget(icon_badge)
        card_layout.addLayout(top_row)

        # Valeur principale
        lbl_value = QLabel("0 élèves")
        lbl_value.setObjectName("statValue")
        lbl_value.setStyleSheet(f"color: {theme.TEXTE};")
        card_layout.addWidget(lbl_value)

        # Sous-titre
        lbl_sub = QLabel("sur 0 inscrits")
        lbl_sub.setObjectName("legendLabel")
        card_layout.addWidget(lbl_sub)

        card_layout.addStretch()

        return {'frame': frame, 'lbl_value': lbl_value, 'lbl_subtitle': lbl_sub}

    def _create_filter_bar(self, parent_layout):
        """Crée la barre de filtres (Recherche avec icône Google Fonts, Classe, Pilules)."""
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        # Recherche avec action icône Google Fonts
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchField")
        self.search_input.setPlaceholderText("Nom ou prénom")
        self.search_input.addAction(get_icon("search", theme.TEXTE_DISCRET, 16), QLineEdit.LeadingPosition)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(220)
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self.filtrer_eleves)
        filter_row.addWidget(self.search_input)

        # Filtre classe
        self.classe_filter = QComboBox()
        self.classe_filter.addItem("Toutes les classes", None)
        self.classe_filter.setFixedWidth(170)
        self.classe_filter.setFixedHeight(36)
        self.charger_classes()
        self.classe_filter.currentIndexChanged.connect(self.filtrer_eleves)
        filter_row.addWidget(self.classe_filter)

        filter_row.addSpacing(6)

        # Chips de filtre par statut
        self._filter_chips = {}
        chip_definitions = [
            ("tous", "Tous 0"),
            ("non_paye", "Non payés 0"),
            ("partiel", "Partiels 0"),
            ("solde", "Soldés 0"),
        ]

        for key, default_text in chip_definitions:
            chip = QPushButton(default_text)
            chip.setObjectName("filterChipActive" if key == "tous" else "filterChip")
            chip.setCursor(Qt.PointingHandCursor)
            chip.setFixedHeight(34)
            chip.clicked.connect(lambda checked, k=key: self._on_chip_clicked(k))
            filter_row.addWidget(chip)
            self._filter_chips[key] = chip

        filter_row.addStretch()
        parent_layout.addLayout(filter_row)

    def _create_action_bar(self, parent_layout):
        """Crée la barre d'actions contextuelle en bas pour l'élève sélectionné."""
        self.action_bar = QFrame()
        self.action_bar.setObjectName("actionBar")
        self.action_bar.setFixedHeight(84)
        self.action_bar.setVisible(False)

        bar_layout = QHBoxLayout(self.action_bar)
        bar_layout.setContentsMargins(18, 12, 18, 12)
        bar_layout.setSpacing(16)

        # Colonne de gauche : Nom sélectionné + Bouton Supprimer en-dessous
        left_col = QVBoxLayout()
        left_col.setSpacing(6)

        self.lbl_selected = QLabel("Élève sélectionné")
        self.lbl_selected.setObjectName("sectionTitle")
        left_col.addWidget(self.lbl_selected)

        # Bouton supprimer rouge outline avec icône Google Fonts "delete"
        self.btn_delete = QPushButton()
        self.btn_delete.setObjectName("dangerOutlineBtn")
        self.btn_delete.setIcon(get_icon("delete", theme.ROUGE, 18))
        self.btn_delete.setIconSize(QSize(18, 18))
        self.btn_delete.setToolTip("Supprimer cet élève")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedSize(38, 32)
        self.btn_delete.clicked.connect(self.on_supprimer)
        left_col.addWidget(self.btn_delete)

        bar_layout.addLayout(left_col)
        bar_layout.addStretch()

        # Boutons d'action à droite avec icônes Google Fonts
        actions_right = QHBoxLayout()
        actions_right.setSpacing(10)

        btn_view = QPushButton("  Voir fiche")
        btn_view.setIcon(get_icon("visibility", theme.TEXTE_SECOND, 18))
        btn_view.setIconSize(QSize(18, 18))
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.setFixedHeight(38)
        btn_view.clicked.connect(self.on_voir_fiche)
        actions_right.addWidget(btn_view)

        btn_edit = QPushButton("  Modifier")
        btn_edit.setIcon(get_icon("edit", theme.TEXTE_SECOND, 18))
        btn_edit.setIconSize(QSize(18, 18))
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setFixedHeight(38)
        btn_edit.clicked.connect(self.on_modifier)
        actions_right.addWidget(btn_edit)

        btn_pay = QPushButton("  Enregistrer paiement")
        btn_pay.setProperty("variant", "primary")
        btn_pay.setIcon(get_icon("payment", "#FFFFFF", 18))
        btn_pay.setIconSize(QSize(18, 18))
        btn_pay.setCursor(Qt.PointingHandCursor)
        btn_pay.setFixedHeight(38)
        btn_pay.clicked.connect(self.on_paiement)
        actions_right.addWidget(btn_pay)

        bar_layout.addLayout(actions_right)
        parent_layout.addWidget(self.action_bar)

    def _on_chip_clicked(self, key: str):
        """Gère le clic sur un chip de statut."""
        self._current_filter = key

        for k, chip in self._filter_chips.items():
            chip.setObjectName("filterChipActive" if k == key else "filterChip")
            chip.style().unpolish(chip)
            chip.style().polish(chip)

        self._appliquer_filtres()

    def _on_selection_changed(self):
        """Affiche ou masque la barre d'action selon la sélection de la table."""
        index = self.table.currentIndex()
        if index.isValid():
            source_index = self.proxy_model.mapToSource(index)
            row = source_index.row()
            nom = self.model.data(self.model.index(row, 0), Qt.DisplayRole) or ""
            self.lbl_selected.setText(f"{nom} sélectionné")
            self.action_bar.setVisible(True)
        else:
            self.action_bar.setVisible(False)

    def charger_classes(self):
        """Charge les classes dans le filtre déroulant."""
        try:
            classes = ClasseService.get_all_classes()
            for classe in classes:
                self.classe_filter.addItem(classe['nom'], classe['id'])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des classes : {e}")

    def charger_donnees(self, annee_id: int = None):
        """
        Charge les données des élèves depuis la base et recalcule les indicateurs.
        
        Args:
            annee_id: Optionnel, filtre par année scolaire
        """
        try:
            self._current_annee_id = annee_id
            self._all_eleves = EleveService.get_all_eleves(annee_id)
            self._update_stat_cards()
            self._appliquer_filtres()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des élèves : {e}")

    def _update_stat_cards(self):
        """Met à jour les cartes statistiques et les compteurs de chips."""
        from services.format_service import formater_montant

        eleves = self._all_eleves
        nb_total = len(eleves)

        total_encaisse = 0
        total_reste = 0
        nb_non_soldes = 0

        for e in eleves:
            montant_du = e.get('montant_total_du', 0)
            solde = e.get('solde', 0)
            paye = montant_du - solde

            total_encaisse += paye
            total_reste += solde

            if e.get('statut') != "Soldé":
                nb_non_soldes += 1

        # Cartes KPI
        self.card_encaisse['lbl_value'].setText(formater_montant(total_encaisse))
        self.card_reste['lbl_value'].setText(formater_montant(total_reste))
        self.card_non_soldes['lbl_value'].setText(f"{nb_non_soldes} élèves")
        self.card_non_soldes['lbl_subtitle'].setText(f"sur {nb_total} inscrits")

        # Barres de progression
        total_attendu = total_encaisse + total_reste
        if total_attendu > 0:
            pct_encaisse = int((total_encaisse / total_attendu) * 100)
            pct_reste = int((total_reste / total_attendu) * 100)
        else:
            pct_encaisse = 0
            pct_reste = 0

        self.card_encaisse['progress'].setValue(pct_encaisse)
        self.card_reste['progress'].setValue(pct_reste)

        # Compteurs pour les chips de filtre
        nb_non_paye = sum(1 for e in eleves if e.get('statut') == "Non payé")
        nb_partiel = sum(1 for e in eleves if e.get('statut') == "Partiellement payé")
        nb_solde = sum(1 for e in eleves if e.get('statut') == "Soldé")

        self._filter_chips["tous"].setText(f"Tous {nb_total}")
        self._filter_chips["non_paye"].setText(f"Non payés {nb_non_paye}")
        self._filter_chips["partiel"].setText(f"Partiels {nb_partiel}")
        self._filter_chips["solde"].setText(f"Soldés {nb_solde}")

    def _appliquer_filtres(self):
        """Applique les filtres de recherche textuelle, classe et statut."""
        texte = self.search_input.text().strip() if hasattr(self, 'search_input') else ""
        classe_id = self.classe_filter.currentData() if hasattr(self, 'classe_filter') else None

        try:
            if texte or classe_id:
                eleves = EleveService.rechercher_eleves(texte, classe_id)
            else:
                eleves = list(self._all_eleves)

            # Filtre par statut
            if self._current_filter == "non_paye":
                eleves = [e for e in eleves if e.get('statut') == "Non payé"]
            elif self._current_filter == "partiel":
                eleves = [e for e in eleves if e.get('statut') == "Partiellement payé"]
            elif self._current_filter == "solde":
                eleves = [e for e in eleves if e.get('statut') == "Soldé"]

            self.model.set_data(eleves)
            self.mettre_a_jour_compteur(len(eleves))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du filtrage : {e}")

    def filtrer_eleves(self):
        """Déclenche le filtrage."""
        self._appliquer_filtres()

    def mettre_a_jour_compteur(self, nb: int):
        """Met à jour le texte de pagination au bas du tableau."""
        total = len(self._all_eleves)
        if nb == 0:
            self.lbl_pagination.setText("0 élève")
        elif nb == total:
            self.lbl_pagination.setText(f"1 à {nb} sur {nb} élèves")
        else:
            self.lbl_pagination.setText(f"1 à {nb} sur {total} élèves")

    def eleve_selectionne_id(self) -> int | None:
        """Récupère l'identifiant de l'élève actuellement sélectionné."""
        index = self.table.currentIndex()
        if not index.isValid():
            return None
        source_index = self.proxy_model.mapToSource(index)
        return self.model.get_eleve_id(source_index.row())

    def on_double_click(self, index):
        """Double-clic sur une ligne ouvre la fiche élève."""
        source_index = self.proxy_model.mapToSource(index)
        eleve_id = self.model.get_eleve_id(source_index.row())
        if eleve_id:
            self.voir_fiche.emit(eleve_id)

    def on_modifier(self):
        """Bouton Modifier."""
        eleve_id = self.eleve_selectionne_id()
        if eleve_id:
            self.modifier_eleve.emit(eleve_id)
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")

    def on_supprimer(self):
        """Bouton Supprimer."""
        eleve_id = self.eleve_selectionne_id()
        if not eleve_id:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")
            return

        from services.eleve_service import EleveService
        try:
            eleve = EleveService.get_eleve_by_id(eleve_id)
            if not eleve:
                QMessageBox.critical(self, "Erreur", "Élève introuvable")
                return

            from services.paiement_service import PaiementService
            paiements = PaiementService.get_paiements_eleve(eleve_id)
            nb_paiements = len(paiements)

            if nb_paiements > 0:
                QMessageBox.warning(
                    self,
                    "Suppression impossible",
                    f"Impossible de supprimer {eleve['prenom']} {eleve['nom']} car il a {nb_paiements} paiement(s) enregistré(s).\n\n"
                    f"Pour supprimer cet élève, vous devez d'abord supprimer ses paiements."
                )
                return

            reponse = QMessageBox.question(
                self,
                "Confirmation de suppression",
                f"Êtes-vous sûr de vouloir supprimer {eleve['prenom']} {eleve['nom']} ({eleve['classe_nom']}) ?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reponse == QMessageBox.Yes:
                EleveService.supprimer_eleve(eleve_id)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"{eleve['prenom']} {eleve['nom']} a été supprimé avec succès."
                )
                self.rafraichir()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def on_paiement(self):
        """Bouton Enregistrer paiement."""
        eleve_id = self.eleve_selectionne_id()
        if eleve_id:
            self.enregistrer_paiement.emit(eleve_id)
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")

    def on_voir_fiche(self):
        """Bouton Voir fiche."""
        eleve_id = self.eleve_selectionne_id()
        if eleve_id:
            self.voir_fiche.emit(eleve_id)
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner un élève")

    def rafraichir(self):
        """Rafraîchit la liste et les indicateurs."""
        self.charger_donnees(self._current_annee_id)
