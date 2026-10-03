"""
Point d'entrée de l'application EduPaie.

Initialise l'application PySide6 et affiche la fenêtre principale.
"""

import sys
import logging
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from ui.style_loader import charger_style, resource_path


def setup_logging():
    """
    Configure le logging de l'application.

    Crée un fichier de log dans le dossier utilisateur de l'application.
    """
    # Déterminer le dossier de logs
    if getattr(sys, 'frozen', False):
        log_dir = Path.home() / "EduPaie" / "logs"
    else:
        log_dir = Path(__file__).parent / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "edupaie.log"

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("=== Démarrage d'EduPaie ===")
    return log_file



def excepthook(exc_type, exc_value, exc_traceback):
    """
    Gestionnaire global des exceptions non capturées.
    
    Affiche une boîte de dialogue d'erreur et journalise l'exception avec détails.
    """
    # Journalisation détaillée
    logging.error(
        "Exception non gérée",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Obtenir le traceback complet
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Affichage d'une boîte de dialogue
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Erreur")
    msg.setText("Une erreur inattendue s'est produite.")
    msg.setInformativeText(str(exc_value))
    msg.setDetailedText(tb_str)
    msg.exec()


def main():
    """Fonction principale de l'application."""
    # Configuration du logging
    log_file = setup_logging()
    
    # Configuration du gestionnaire d'exceptions global
    sys.excepthook = excepthook
    
    try:
        # Création de l'application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Style cohérent sur toutes les plateformes

        # Configuration de l'application
        app.setApplicationName("EduPaie")
        app.setOrganizationName("EduPaie")

        # Configurer l'icône de l'application (Windows)
        if sys.platform == "win32":
            import ctypes
            from PySide6.QtGui import QIcon
            # Identifiant propre à l'application : sans lui, Windows regroupe la fenêtre
            # sous l'icône de Python dans la barre des tâches.
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("edupaie.gestion.paiements")
            app.setWindowIcon(QIcon(str(resource_path("assets/icon.ico"))))

        # Charger la feuille de style et les polices d'icônes
        charger_style(app)
        from ui.icons import charger_police_icones
        charger_police_icones()

        logging.info("Initialisation de l'interface...")

        # Affichage de la fenêtre principale
        window = MainWindow()
        window.show()

        logging.info("Application démarrée avec succès")

        # Boucle d'événements
        sys.exit(app.exec())
        
    except Exception as e:
        logging.critical(f"Erreur critique au démarrage : {e}", exc_info=True)
        # Afficher une boîte de dialogue même si l'interface n'a pas pu démarrer
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erreur critique")
        msg.setText("L'application n'a pas pu démarrer.")
        msg.setInformativeText(str(e))
        msg.setDetailedText(traceback.format_exc())
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()