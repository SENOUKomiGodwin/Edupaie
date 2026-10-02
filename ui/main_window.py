"""
Fenêtre principale de l'application EduPaie.

Contient la barre latérale de navigation stylisée et la zone de contenu.
Design moderne avec icônes Google Fonts (Material Icons) sans emoji,
options de menu épurées (Tableau de bord et Élèves).
"""

import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QMessageBox, QDialog,
    QLabel, QFrame, QSizePolicy, QApplication, QComboBox
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont
from config import APP_NAME, APP_VERSION
from ui.widgets.dashboard_widget import DashboardWidget
from ui.widgets.eleve_list_widget import EleveListWidget
from ui.widgets.eleve_fiche_widget import EleveFicheWidget
from data.database import initialize_database
from services.annee_service import AnneeService
from ui import theme
from ui.icons import get_icon, creer_label_icone


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application EduPaie."""

    # Signal émis quand l'année scolaire change
    annee_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1180, 780)
        self._nav_buttons = []
        self._nav_badges = []
        self._nav_icons = ["dashboard", "people"]
        self._current_nav_index = 1  # Défaut sur "Élèves" comme sur la maquette
        self._current_annee_id = None

        # Initialiser la base de données
        try:
            initialize_database()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'initialisation de la base de données : {e}"
            )

        self.setup_ui()
        # Sélectionner "Élèves" par défaut
        self.on_navigation_changed(1)

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        # 1. Barre latérale
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # 2. Zone de contenu (cartes et écrans)
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        # Création des écrans
        self.dashboard = DashboardWidget()
        self.eleve_list = EleveListWidget()
        self.eleve_fiche = EleveFicheWidget()

        self.content_stack.addWidget(self.dashboard)     # Index 0
        self.content_stack.addWidget(self.eleve_list)    # Index 1
        self.content_stack.addWidget(self.eleve_fiche)   # Index 2

        # Connexions des signaux
        self.eleve_list.nouveau_eleve.connect(self.on_nouveau_eleve)
        self.eleve_list.modifier_eleve.connect(self.on_modifier_eleve)
        self.eleve_list.supprimer_eleve.connect(self.on_supprimer_eleve)
        self.eleve_list.enregistrer_paiement.connect(self.on_enregistrer_paiement)
        self.eleve_list.voir_fiche.connect(self.on_voir_fiche)
        self.eleve_fiche.fermer_fiche.connect(self.on_fermer_fiche)
        self.eleve_fiche.reimprimer_recu.connect(self.on_reimprimer_recu)
        
        # Connexion du changement d'année scolaire
        self.annee_changed.connect(self.eleve_list.charger_donnees)
        self.annee_changed.connect(self.dashboard.charger_statistiques)

    def _create_sidebar(self) -> QWidget:
        """Crée la barre latérale blanche aux coins arrondis avec icônes Google Fonts."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(0)

        # --- Logo et identité ---
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)

        # Icône carrée émeraude avec icône Google Fonts "school"
        icon_box = QFrame()
        icon_box.setFixedSize(36, 36)
        icon_box.setStyleSheet("""
            background-color: #047857;
            border-radius: 8px;
        """)
        ib_layout = QVBoxLayout(icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        school_icon = creer_label_icone("school", "#FFFFFF", 20)
        ib_layout.addWidget(school_icon, 0, Qt.AlignCenter)
        logo_layout.addWidget(icon_box)

        # Textes du logo
        name_layout = QVBoxLayout()
        name_layout.setSpacing(1)
        app_name = QLabel("EduPaie")
        app_name.setObjectName("appName")
        name_layout.addWidget(app_name)
        app_subtitle = QLabel("Gestion scolaire")
        app_subtitle.setObjectName("appSubtitle")
        name_layout.addWidget(app_subtitle)
        logo_layout.addLayout(name_layout)
        logo_layout.addStretch()

        layout.addWidget(logo_frame)
        layout.addSpacing(18)

        # --- Sélecteur d'année scolaire ---
        year_frame = QFrame()
        year_frame.setObjectName("yearSelector")
        year_layout = QVBoxLayout(year_frame)
        year_layout.setContentsMargins(12, 8, 12, 8)
        year_layout.setSpacing(2)

        year_label = QLabel("Année scolaire")
        year_label.setObjectName("yearLabel")
        year_layout.addWidget(year_label)

        # QComboBox pour sélectionner l'année
        self.year_combo = QComboBox()
        self.year_combo.setObjectName("yearCombo")
        self.year_combo.setFixedHeight(36)
        
        # Charger les années scolaires
        try:
            annees = AnneeService.get_all_annees()
            self.annee_id_to_index = {}  # Mapping id -> index
            
            for i, annee in enumerate(annees):
                self.year_combo.addItem(annee['libelle'], annee['id'])
                self.annee_id_to_index[annee['id']] = i
                
                # Sélectionner l'année active par défaut
                if annee.get('active', False):
                    self.year_combo.setCurrentIndex(i)
                    self._current_annee_id = annee['id']
        except Exception as e:
            logging.error(f"Erreur lors du chargement des années: {e}")
            self.year_combo.addItem("2024-2025", 1)
            self._current_annee_id = 1
        
        # Connexion du changement d'année
        self.year_combo.currentIndexChanged.connect(self.on_annee_changed)
        
        year_layout.addWidget(self.year_combo)
        
        # Bouton pour créer une nouvelle année
        new_year_btn = QPushButton("+ Nouvelle année")
        new_year_btn.setObjectName("newYearBtn")
        new_year_btn.setFixedHeight(28)
        new_year_btn.clicked.connect(self.on_creer_nouvelle_annee)
        year_layout.addWidget(new_year_btn)

        layout.addWidget(year_frame)
        layout.addSpacing(22)

        # --- Section MENU ---
        menu_label = QLabel("MENU")
        menu_label.setObjectName("menuLabel")
        layout.addWidget(menu_label)
        layout.addSpacing(8)

        # Éléments de navigation (uniquement Tableau de bord et Élèves)
        nav_definitions = [
            ("Tableau de bord", "dashboard", False),
            ("Élèves", "people", True),
        ]

        for i, (label_text, icon_name, has_badge) in enumerate(nav_definitions):
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(container)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)

            btn = QPushButton(f"  {label_text}")
            btn.setObjectName("navItem")
            btn.setIcon(get_icon(icon_name, theme.TEXTE_SECOND, 18))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, idx=i: self.on_navigation_changed(idx))
            row_layout.addWidget(btn, 1)

            badge = QLabel("")
            badge.setObjectName("navBadgeInactive")
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(30, 20)
            badge.setVisible(False)
            row_layout.addWidget(badge)

            self._nav_buttons.append(btn)
            self._nav_badges.append(badge)

            layout.addWidget(container)
            layout.addSpacing(4)

        layout.addStretch()

        # --- Section utilisateur en bas ---
        user_section = QFrame()
        user_section.setObjectName("userSection")
        user_layout = QHBoxLayout(user_section)
        user_layout.setContentsMargins(0, 14, 0, 0)
        user_layout.setSpacing(10)

        avatar = QLabel("SE")
        avatar.setObjectName("userAvatar")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        user_name = QLabel("Secrétariat")
        user_name.setObjectName("userName")
        user_info.addWidget(user_name)
        user_version = QLabel(f"v{APP_VERSION}")
        user_version.setObjectName("userRole")
        user_info.addWidget(user_version)
        user_layout.addLayout(user_info)
        user_layout.addStretch()

        layout.addWidget(user_section)

        return sidebar

    def _update_nav_state(self, active_index: int):
        """Met à jour les styles et les couleurs d'icônes de navigation."""
        for i, btn in enumerate(self._nav_buttons):
            badge = self._nav_badges[i]
            icon_name = self._nav_icons[i]
            if i == active_index:
                btn.setObjectName("navItemActive")
                btn.setIcon(get_icon(icon_name, theme.VERT_TEXTE, 18))
                badge.setObjectName("navBadge")
            else:
                btn.setObjectName("navItem")
                btn.setIcon(get_icon(icon_name, theme.TEXTE_SECOND, 18))
                badge.setObjectName("navBadgeInactive")

            btn.style().unpolish(btn)
            btn.style().polish(btn)
            badge.style().unpolish(badge)
            badge.style().polish(badge)

        self._current_nav_index = active_index

    def _update_eleve_badge(self):
        """Met à jour le badge d'effectif d'élèves sur le bouton Élèves."""
        try:
            from services.eleve_service import EleveService
            eleves = EleveService.get_all_eleves(self._current_annee_id)
            count = len(eleves)
            badge = self._nav_badges[1]  # Élèves
            badge.setText(str(count))
            badge.setVisible(count > 0)
        except Exception:
            pass

    def on_navigation_changed(self, index: int):
        """Gère le changement d'écran lors du clic sur le menu."""
        self._update_nav_state(index)
        self._update_eleve_badge()

        if index == 0:  # Tableau de bord
            self.dashboard.charger_statistiques()
            self.content_stack.setCurrentWidget(self.dashboard)
        elif index == 1:  # Élèves
            self.eleve_list.rafraichir()
            self.content_stack.setCurrentWidget(self.eleve_list)

    def on_nouveau_eleve(self):
        """Ouvre le formulaire d'ajout d'élève."""
        from ui.widgets.eleve_form_widget import EleveFormDialog
        dialog = EleveFormDialog(self, default_annee_id=self._current_annee_id)
        if dialog.exec() == QDialog.Accepted:
            self.eleve_list.rafraichir()
            self._update_eleve_badge()

    def on_modifier_eleve(self, eleve_id: int):
        """Ouvre le formulaire de modification d'un élève."""
        from ui.widgets.eleve_form_widget import EleveFormDialog
        dialog = EleveFormDialog(self, eleve_id)
        if dialog.exec() == QDialog.Accepted:
            self.eleve_list.rafraichir()

    def on_enregistrer_paiement(self, eleve_id: int):
        """Ouvre le dialogue d'enregistrement de paiement."""
        from ui.widgets.paiement_dialog import PaiementDialog
        dialog = PaiementDialog(self, eleve_id)
        dialog.paiement_enregistre.connect(self.eleve_list.rafraichir)
        dialog.exec()

    def on_voir_fiche(self, eleve_id: int):
        """Affiche la fiche détaillée d'un élève."""
        self.eleve_fiche.set_eleve(eleve_id)
        self.content_stack.setCurrentWidget(self.eleve_fiche)

    def on_fermer_fiche(self):
        """Ferme la fiche détaillée et retourne à la liste."""
        self.content_stack.setCurrentWidget(self.eleve_list)

    def on_reimprimer_recu(self, paiement_id: int):
        """Génère et propose d'ouvrir le reçu PDF."""
        from services.recu_service import RecuService
        import os

        try:
            pdf_path = RecuService.generer_pdf(paiement_id)
            reponse = QMessageBox.question(
                self,
                "Reçu généré",
                f"Le reçu a été généré :\n{pdf_path}\n\n"
                "Voulez-vous ouvrir le fichier ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reponse == QMessageBox.Yes:
                os.startfile(pdf_path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la génération du reçu : {e}"
            )

    def on_supprimer_eleve(self, eleve_id: int):
        """Supprime un élève si aucun paiement n'y est rattaché."""
        try:
            from services.eleve_service import EleveService
            succes = EleveService.supprimer_eleve(eleve_id)
            if succes:
                QMessageBox.information(self, "Succès", "L'élève a été supprimé avec succès")
                self.eleve_list.rafraichir()
                self._update_eleve_badge()
            else:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Impossible de supprimer cet élève car il a des paiements enregistrés"
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def on_annee_changed(self, index: int):
        """Gère le changement d'année scolaire."""
        if index < 0:
            return
        
        annee_id = self.year_combo.currentData()
        if annee_id and annee_id != self._current_annee_id:
            self._current_annee_id = annee_id
            logging.info(f"Année scolaire changée vers ID: {annee_id}")
            
            # Émettre le signal pour les widgets
            self.annee_changed.emit(annee_id)
            
            # Rafraîchir les données
            self.eleve_list.charger_donnees(annee_id)
            self.dashboard.charger_statistiques(annee_id)
            self._update_eleve_badge()

    def on_creer_nouvelle_annee(self):
        """Ouvre un dialogue pour créer une nouvelle année scolaire."""
        from PySide6.QtWidgets import QInputDialog
        from services.annee_service import AnneeService
        
        # Demander le libellé de la nouvelle année
        libelle, ok = QInputDialog.getText(
            self,
            "Nouvelle année scolaire",
            "Entrez le libellé de l'année scolaire (ex: 2025-2026) :",
            text="2025-2026"
        )
        
        if ok and libelle:
            try:
                annee_id = AnneeService.creer_annee(libelle)
                QMessageBox.information(
                    self,
                    "Succès",
                    f"L'année scolaire '{libelle}' a été créée avec succès"
                )
                
                # Recharger le combo
                self.recharger_annees()
                
                # Sélectionner la nouvelle année
                if annee_id in self.annee_id_to_index:
                    self.year_combo.setCurrentIndex(self.annee_id_to_index[annee_id])
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la création de l'année : {e}"
                )

    def recharger_annees(self):
        """Recharge la liste des années scolaires dans le combo."""
        try:
            annees = AnneeService.get_all_annees()
            self.year_combo.clear()
            self.annee_id_to_index = {}
            
            for i, annee in enumerate(annees):
                self.year_combo.addItem(annee['libelle'], annee['id'])
                self.annee_id_to_index[annee['id']] = i
                
                if annee.get('active', False):
                    self.year_combo.setCurrentIndex(i)
                    self._current_annee_id = annee['id']
                    
        except Exception as e:
            logging.error(f"Erreur lors du rechargement des années: {e}")
