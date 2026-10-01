"""
Dialogue d'enregistrement de paiement.

Permet d'enregistrer un paiement pour un élève, avec récapitulatif du solde.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QSpinBox, QDateEdit,
    QFormLayout, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from services.recu_service import RecuService
from services.validation_service import ValidationError
from config import MODES_PAIEMENT, FORMAT_DATE


class PaiementDialog(QDialog):
    """Dialogue d'enregistrement de paiement."""

    # Signal émis lors d'un paiement réussi
    paiement_enregistre = Signal()

    def __init__(self, parent=None, eleve_id=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(480)
        self.setup_ui()

        if eleve_id:
            self.charger_eleve()

    def setup_ui(self):
        """Configure l'interface du dialogue."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(16)

        # ----- Carte récapitulatif élève -----
        carte_eleve = QFrame()
        carte_eleve.setObjectName("card")
        eleve_layout = QVBoxLayout(carte_eleve)
        eleve_layout.setContentsMargins(16, 14, 16, 14)
        eleve_layout.setSpacing(4)

        self.eleve_info = QLabel("Élève : ")
        self.eleve_info.setStyleSheet("font-weight: bold; font-size: 15px;")
        eleve_layout.addWidget(self.eleve_info)

        self.solde_info = QLabel("Solde restant : ")
        self.solde_info.setStyleSheet("font-weight: bold; color: #DC2626;")
        eleve_layout.addWidget(self.solde_info)

        layout.addWidget(carte_eleve)

        # ----- Carte formulaire -----
        carte_form = QFrame()
        carte_form.setObjectName("card")
        carte_form_layout = QVBoxLayout(carte_form)
        carte_form_layout.setContentsMargins(20, 18, 20, 18)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Montant
        montant_layout = QHBoxLayout()
        self.montant_input = QSpinBox()
        self.montant_input.setRange(1, 999999999)
        self.montant_input.setSingleStep(1000)
        self.montant_input.setMinimumWidth(180)
        montant_layout.addWidget(self.montant_input)
        lbl_fcfa = QLabel("FCFA")
        lbl_fcfa.setStyleSheet("color: #666; font-weight: 500;")
        montant_layout.addWidget(lbl_fcfa)
        montant_layout.addStretch()
        form.addRow("Montant", montant_layout)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setMinimumWidth(220)
        form.addRow("Date", self.date_input)

        # Mode de paiement
        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumWidth(220)
        self.charger_modes_paiement()
        form.addRow("Mode de paiement", self.mode_combo)

        carte_form_layout.addLayout(form)
        layout.addWidget(carte_form)

        # ----- Boutons -----
        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)

        buttons.addStretch()

        self.btn_validate = QPushButton("Valider le paiement")
        self.btn_validate.setProperty("variant", "primary")
        self.btn_validate.setDefault(True)
        self.btn_validate.clicked.connect(self.on_valider)
        buttons.addWidget(self.btn_validate)

        layout.addLayout(buttons)

    def charger_modes_paiement(self):
        """Charge les modes de paiement depuis la configuration."""
        for mode_key, mode_libelle in MODES_PAIEMENT.items():
            self.mode_combo.addItem(mode_libelle, mode_key)

    def charger_eleve(self):
        """Charge les informations de l'élève."""
        from PySide6.QtWidgets import QMessageBox

        try:
            eleve = EleveService.get_eleve_by_id(self.eleve_id)
            if eleve:
                self.eleve_info.setText(
                    f"Élève : {eleve['prenom']} {eleve['nom']} ({eleve['classe_nom']})"
                )
                self.solde_info.setText(f"Solde restant : {eleve['solde_formate']}")

                # Limiter le montant maximal au solde
                self.montant_input.setMaximum(max(1, eleve['solde']))

                # Si soldé, désactiver le formulaire
                if eleve['solde'] <= 0:
                    self.montant_input.setEnabled(False)
                    self.btn_validate.setEnabled(False)
                    QMessageBox.information(
                        self,
                        "Information",
                        "Cet élève est déjà soldé. Aucun paiement nécessaire."
                    )
            else:
                QMessageBox.critical(self, "Erreur", "Élève introuvable")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement de l'élève : {e}")
            self.reject()

    def on_valider(self):
        """Gère la validation du paiement."""
        from PySide6.QtWidgets import QMessageBox
        import logging

        montant = self.montant_input.value()
        date = self.date_input.date().toPython()
        mode = self.mode_combo.currentData()

        # Validation
        if montant <= 0:
            QMessageBox.warning(self, "Attention", "Le montant doit être positif")
            return

        try:
            # Enregistrer le paiement
            paiement_id = PaiementService.enregistrer_paiement(
                self.eleve_id,
                montant,
                date,
                mode
            )

            # Générer automatiquement le PDF
            try:
                RecuService.generer_pdf(paiement_id)
            except Exception as e:
                logging.exception("Erreur lors de la génération du PDF")
                QMessageBox.warning(
                    self,
                    "Attention",
                    f"Erreur lors de la génération du PDF : {e}"
                )

            QMessageBox.information(
                self,
                "Succès",
                f"Le paiement a été enregistré avec succès.\n"
                f"Numéro de reçu : REC-{date.year:04d}-{paiement_id:06d}"
            )

            self.paiement_enregistre.emit()
            self.accept()

        except ValidationError as e:
            QMessageBox.warning(self, "Erreur de validation", str(e))
        except Exception as e:
            logging.exception("Erreur inattendue lors de l'enregistrement du paiement")
            QMessageBox.critical(self, "Erreur", f"Une erreur inattendue s'est produite : {e}")
