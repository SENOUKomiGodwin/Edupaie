"""
Service de génération de reçus PDF.

Génère des reçus PDF avec reportlab et gère l'impression.
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from data.repositories.paiement_repository import PaiementRepository
from data.repositories.eleve_repository import EleveRepository
from services.format_service import montant_en_lettres, formater_montant
from config import DEVISE, MODES_PAIEMENT


class RecuService:
    """Service pour la génération de reçus."""
    
    @staticmethod
    def generer_pdf(paiement_id: int, chemin_sortie: str = None) -> str:
        """
        Génère un reçu PDF pour un paiement.
        
        Args:
            paiement_id: ID du paiement
            chemin_sortie: Chemin du fichier de sortie (optionnel)
            
        Returns:
            Chemin du fichier PDF généré
        """
        # Récupérer les données du paiement
        paiement = PaiementRepository.get_by_id(paiement_id)
        if not paiement:
            raise ValueError("Paiement introuvable")
        
        eleve = EleveRepository.get_by_id(paiement['eleve_id'])
        if not eleve:
            raise ValueError("Élève introuvable")
        
        # Définir le chemin de sortie
        if chemin_sortie is None:
            from data.database import get_database_path
            db_dir = get_database_path().parent
            db_dir.mkdir(parents=True, exist_ok=True)
            chemin_sortie = db_dir / f"recu_{paiement['numero_recu']}.pdf"
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            str(chemin_sortie),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Créer les styles
        styles = getSampleStyleSheet()
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # centré
        )
        
        # Contenu du reçu
        elements = []
        
        # Titre
        elements.append(Paragraph("REÇU DE PAIEMENT", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Numéro de reçu
        elements.append(Paragraph(f"<b>Numéro de reçu :</b> {paiement['numero_recu']}", styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # Informations de l'école (placeholder)
        elements.append(Paragraph("<b>ÉCOLE :</b> [Nom de l'école]", styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tableau des informations
        data = [
            ["Informations élève", ""],
            ["Nom :", f"{eleve['nom']} {eleve['prenom']}"],
            ["Classe :", f"{eleve['classe_nom']}"],
            ["Année scolaire :", f"{eleve['annee_libelle']}"],
            ["", ""],
            ["Informations paiement", ""],
            ["Date de paiement :", paiement['date_paiement']],
            ["Montant payé :", formater_montant(paiement['montant'])],
            ["Mode de paiement :", MODES_PAIEMENT.get(paiement['mode'], paiement['mode'])],
            ["Solde après paiement :", formater_montant(paiement['solde_apres'])],
        ]
        
        table = Table(data, colWidths=[5*cm, 8*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('LINEABOVE', (0, 5), (-1, 5), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        # Montant en toutes lettres
        montant_lettres = montant_en_lettres(paiement['montant'])
        elements.append(Paragraph(f"<b>Montant en lettres :</b> {montant_lettres}", styles['Normal']))
        elements.append(Spacer(1, 1*cm))
        
        # Signature
        elements.append(Paragraph("Signature du caissier : ____________________", styles['Normal']))
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph("Date d'émission : " + paiement['date_paiement'], styles['Normal']))
        
        # Générer le PDF
        doc.build(elements)
        
        return str(chemin_sortie)
    
    @staticmethod
    def imprimer_recu(paiement_id: int):
        """
        Imprime directement un reçu via QPrinter.
        
        Args:
            paiement_id: ID du paiement
        """
        from PySide6.QtWidgets import QPrintDialog, QPrinter
        from PySide6.QtCore import QUrl
        from PySide6.QtWebEngineWidgets import QWebEngineView
        import tempfile
        
        # Générer le PDF
        pdf_path = RecuService.generer_pdf(paiement_id)
        
        # Afficher la boîte de dialogue d'impression
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer)
        
        if dialog.exec() == QPrintDialog.Accepted:
            # Pour l'impression directe, nous utiliserions QPdfDocument
            # Pour l'instant, on informe l'utilisateur
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Information",
                f"Le reçu a été généré :\n{pdf_path}\n\n"
                "L'impression directe nécessite une configuration supplémentaire.\n"
                "Vous pouvez ouvrir le fichier PDF et l'imprimer depuis votre lecteur PDF."
            )
