"""
Fenêtre principale de l'application EduPaie.

Contient la barre latérale de navigation et les différents écrans.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QListWidget, QListWidgetItem, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from config import APP_NAME, APP_VERSION
from ui.widgets.dashboard_widget import DashboardWidget
from ui.widgets.eleve_list_widget import EleveListWidget
from ui.widgets.eleve_fiche_widget import EleveFicheWidget
from data.database import initialize_database


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1024, 768)
        
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
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Barre latérale
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 1)
        
        # Zone de contenu
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 4)
        
        # Créer les widgets
        self.dashboard = DashboardWidget()
        self.eleve_list = EleveListWidget()
        self.eleve_fiche = EleveFicheWidget()
        
        # Ajouter les widgets au stack
        self.content_stack.addWidget(self.dashboard)
        self.content_stack.addWidget(self.eleve_list)
        self.content_stack.addWidget(self.eleve_fiche)
        
        # Connecter les signaux
        self.eleve_list.nouveau_eleve.connect(self.on_nouveau_eleve)
        self.eleve_list.modifier_eleve.connect(self.on_modifier_eleve)
        self.eleve_list.supprimer_eleve.connect(self.on_supprimer_eleve)
        self.eleve_list.enregistrer_paiement.connect(self.on_enregistrer_paiement)
        self.eleve_list.voir_fiche.connect(self.on_voir_fiche)
        self.eleve_fiche.fermer_fiche.connect(self.on_fermer_fiche)
        self.eleve_fiche.reimprimer_recu.connect(self.on_reimprimer_recu)
    
    def create_sidebar(self) -> QWidget:
        """
        Crée la barre latérale de navigation.
        
        Returns:
            Widget de la barre latérale
        """
        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)
        
        # Liste de navigation
        nav_list = QListWidget()
        nav_list.addItem("Tableau de bord")
        nav_list.addItem("Élèves")
        nav_list.currentRowChanged.connect(self.on_navigation_changed)
        
        layout.addWidget(nav_list)
        layout.addStretch()
        
        return sidebar
    
    def on_navigation_changed(self, index):
        """
        Gère le changement de navigation.
        
        Args:
            index: Index de l'élément sélectionné
        """
        if index == 0:  # Tableau de bord
            self.dashboard.charger_statistiques()
            self.content_stack.setCurrentWidget(self.dashboard)
        elif index == 1:  # Élèves
            self.content_stack.setCurrentWidget(self.eleve_list)
        else:
            self.content_stack.setCurrentIndex(index)
    
    def on_nouveau_eleve(self):
        """Gère la création d'un nouvel élève."""
        from ui.widgets.eleve_form_widget import EleveFormDialog
        dialog = EleveFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.eleve_list.rafraichir()
    
    def on_modifier_eleve(self, eleve_id):
        """
        Gère la modification d'un élève.
        
        Args:
            eleve_id: ID de l'élève à modifier
        """
        from ui.widgets.eleve_form_widget import EleveFormDialog
        dialog = EleveFormDialog(self, eleve_id)
        if dialog.exec() == QDialog.Accepted:
            self.eleve_list.rafraichir()
    
    def on_enregistrer_paiement(self, eleve_id):
        """
        Gère l'enregistrement d'un paiement.
        
        Args:
            eleve_id: ID de l'élève
        """
        from ui.widgets.paiement_dialog import PaiementDialog
        dialog = PaiementDialog(self, eleve_id)
        dialog.paiement_enregistre.connect(self.eleve_list.rafraichir)
        dialog.exec()
    
    def on_voir_fiche(self, eleve_id):
        """
        Gère l'affichage de la fiche élève.
        
        Args:
            eleve_id: ID de l'élève
        """
        self.eleve_fiche.set_eleve(eleve_id)
        self.content_stack.setCurrentWidget(self.eleve_fiche)
    
    def on_fermer_fiche(self):
        """Gère la fermeture de la fiche élève."""
        self.content_stack.setCurrentWidget(self.eleve_list)
    
    def on_reimprimer_recu(self, paiement_id):
        """
        Gère la ré-impression d'un reçu.
        
        Args:
            paiement_id: ID du paiement
        """
        from services.recu_service import RecuService
        from PySide6.QtWidgets import QMessageBox, QFileDialog
        
        try:
            # Générer le PDF
            pdf_path = RecuService.generer_pdf(paiement_id)
            
            # Demander à l'utilisateur s'il veut ouvrir le fichier
            reponse = QMessageBox.question(
                self,
                "Reçu généré",
                f"Le reçu a été généré :\n{pdf_path}\n\n"
                "Voulez-vous ouvrir le fichier ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reponse == QMessageBox.Yes:
                import os
                os.startfile(pdf_path)  # Windows
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la génération du reçu : {e}"
            )
    
    def on_supprimer_eleve(self, eleve_id):
        """
        Gère la suppression d'un élève.
        
        Args:
            eleve_id: ID de l'élève à supprimer
        """
        try:
            from services.eleve_service import EleveService
            succes = EleveService.supprimer_eleve(eleve_id)
            
            if succes:
                QMessageBox.information(self, "Succès", "L'élève a été supprimé avec succès")
                self.eleve_list.rafraichir()
            else:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Impossible de supprimer cet élève car il a des paiements enregistrés"
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")
