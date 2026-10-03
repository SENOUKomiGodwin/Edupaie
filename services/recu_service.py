"""
Service de génération de reçus PDF.

Génère des reçus PDF avec reportlab canvas et gère l'impression.
"""

import math
from pathlib import Path
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from data.repositories.paiement_repository import PaiementRepository
from data.repositories.eleve_repository import EleveRepository
from services.format_service import montant_en_lettres, formater_montant
from config import DEVISE, MODES_PAIEMENT, NOM_ECOLE, ADRESSE_ECOLE, TEL_ECOLE

# Couleurs
ENCRE = colors.HexColor("#12261F")
VERT = colors.HexColor("#1F9D63")
PAPIER = colors.HexColor("#F6F6F1")


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
        
        # Calculer le déjà versé
        total_du = eleve['montant_total_du']
        solde_apres = paiement['solde_apres']
        deja_verse = total_du - solde_apres
        
        # Créer le document PDF
        pagesize = landscape(A5)
        c = canvas.Canvas(str(chemin_sortie), pagesize=pagesize)
        
        # Marges intérieures 10 mm
        margin = 10 * mm
        width, height = pagesize
        
        # Fond de la page
        c.setFillColor(PAPIER)
        c.rect(0, 0, width, height, fill=True, stroke=False)
        
        # a) Triangle haut-gauche (55 mm de côté) - contour uniquement
        triangle_size = 55 * mm
        c.setStrokeColor(ENCRE)
        c.setLineWidth(1)
        c.line(margin, height - margin, margin + triangle_size, height - margin)
        c.line(margin + triangle_size, height - margin, margin, height - margin - triangle_size)
        c.line(margin, height - margin - triangle_size, margin, height - margin)
        
        # Bande diagonale verte à 35% d'opacité (ligne diagonale)
        c.setStrokeColor(VERT)
        c.setLineWidth(triangle_size * 0.3)
        c.line(margin, height - margin, margin, height - margin - triangle_size)
        c.setLineWidth(1)
        
        # Hexagone du logo au centre du triangle
        hex_center_x = margin + triangle_size / 2
        hex_center_y = height - margin - triangle_size / 2
        hex_radius = 15 * mm
        
        c.setStrokeColor(VERT)
        c.setLineWidth(1.5)
        c.setFillColor(PAPIER)
        
        # Dessiner l'hexagone avec des lignes
        hex_points = []
        for i in range(6):
            angle = 30 + i * 60
            angle_rad = angle * math.pi / 180
            x = hex_center_x + hex_radius * math.cos(angle_rad)
            y = hex_center_y + hex_radius * math.sin(angle_rad)
            hex_points.append((x, y))
        
        # Dessiner le contour de l'hexagone
        for i in range(6):
            x1, y1 = hex_points[i]
            x2, y2 = hex_points[(i + 1) % 6]
            c.line(x1, y1, x2, y2)
        
        # Remplir l'hexagone (approximation avec cercle)
        c.setFillColor(PAPIER)
        c.circle(hex_center_x, hex_center_y, hex_radius * 0.9, fill=1, stroke=0)
        
        # Logo ou texte "Logo"
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            try:
                c.drawImage(str(logo_path), hex_center_x - 10*mm, hex_center_y - 10*mm, 
                           width=20*mm, height=20*mm, mask='auto')
            except:
                c.setFont("Helvetica", 10)
                c.setFillColor(ENCRE)
                c.drawCentredString(hex_center_x, hex_center_y - 3, "Logo")
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(ENCRE)
            c.drawCentredString(hex_center_x, hex_center_y - 3, "Logo")
        
        # b) Cartouche "Reçu de paiement" au centre haut
        c.setFillColor(PAPIER)
        c.setStrokeColor(ENCRE)
        c.setLineWidth(1.2)
        box_width = 120 * mm
        box_height = 15 * mm
        box_x = (width - box_width) / 2
        box_y = height - margin - 30 * mm
        c.roundRect(box_x, box_y, box_width, box_height, 5*mm, fill=True, stroke=True)
        
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(VERT)
        c.drawCentredString(width / 2, box_y + box_height / 2 - 8, "Reçu de paiement")
        
        # c) Informations de l'école haut-droite
        ecole_x = width - margin
        ecole_y = height - margin
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(ENCRE)
        c.drawRightString(ecole_x, ecole_y - 5, NOM_ECOLE)
        
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.Color(0.2, 0.2, 0.2))
        c.drawRightString(ecole_x, ecole_y - 20, ADRESSE_ECOLE)
        c.drawRightString(ecole_x, ecole_y - 30, TEL_ECOLE)
        
        # e) Lignes de saisie en pointillés
        y_pos = height - margin - 60 * mm
        line_width = 100 * mm
        
        c.setFont("Times-Italic", 11)
        c.setFillColor(ENCRE)
        
        # N° du reçu : [numéro]      Date : [date]
        c.drawString(margin, y_pos, "N° du reçu : ")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin + 30*mm, y_pos, paiement['numero_recu'])
        
        c.setFont("Times-Italic", 11)
        c.drawString(width / 2 + 10*mm, y_pos, "Date : ")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(width / 2 + 35*mm, y_pos, paiement['date_paiement'])
        
        # Ligne pointillée
        c.setStrokeColor(ENCRE)
        c.setLineWidth(0.5)
        c.setDash(1, 2)
        c.line(margin, y_pos - 5, width - margin, y_pos - 5)
        c.setDash()
        
        y_pos -= 15 * mm
        
        # Reçu de : Nom Prénom · Classe · Année
        c.setFont("Times-Italic", 11)
        eleve_text = f"{eleve['nom']} {eleve['prenom']} · {eleve['classe_nom']} · {eleve['annee_libelle']}"
        
        # Vérifier si le texte dépasse
        c.setFont("Helvetica-Bold", 11)
        text_width = c.stringWidth(eleve_text, "Helvetica-Bold", 11)
        if text_width > line_width:
            # Réduire la police
            font_size = 11 * line_width / text_width
            c.setFont("Helvetica-Bold", font_size)
        else:
            c.setFont("Helvetica-Bold", 11)
        
        c.drawString(margin, y_pos, "Reçu de ")
        c.drawString(margin + 20*mm, y_pos, eleve_text)
        
        c.line(margin, y_pos - 5, width - margin, y_pos - 5)
        
        y_pos -= 15 * mm
        
        # La somme de : [montant en lettres]
        c.setFont("Times-Italic", 11)
        c.drawString(margin, y_pos, "La somme de ")
        
        montant_lettres = montant_en_lettres(paiement['montant'])
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin + 25*mm, y_pos, montant_lettres)
        
        c.line(margin, y_pos - 5, width - margin, y_pos - 5)
        
        y_pos -= 15 * mm
        
        # Mode de paiement avec cases
        c.setFont("Times-Italic", 11)
        c.drawString(margin, y_pos, "Mode de paiement : ")
        
        modes = ["Espèces", "Chèque", "Virement", "Mobile money"]
        mode_actuel = MODES_PAIEMENT.get(paiement['mode'], paiement['mode'])
        
        box_x = margin + 40 * mm
        box_size = 5 * mm
        spacing = 25 * mm
        
        for i, mode in enumerate(modes):
            # Dessiner la case
            c.setStrokeColor(ENCRE)
            c.setLineWidth(0.5)
            c.rect(box_x + i * spacing, y_pos - 3, box_size, box_size)
            
            c.setFont("Helvetica", 9)
            c.drawString(box_x + i * spacing + box_size + 2, y_pos, mode)
            
            # Cocher la case si c'est le mode actuel
            if mode == mode_actuel:
                # Dessiner un X avec deux lignes
                c.setStrokeColor(ENCRE)
                c.setLineWidth(0.8)
                c.line(box_x + i * spacing, y_pos - 3, 
                       box_x + i * spacing + box_size, y_pos - 3 + box_size)
                c.line(box_x + i * spacing + box_size, y_pos - 3, 
                       box_x + i * spacing, y_pos - 3 + box_size)
        
        c.line(margin, y_pos - 10, width - margin, y_pos - 10)
        
        y_pos -= 20 * mm
        
        # Motif
        c.setFont("Times-Italic", 11)
        c.drawString(margin, y_pos, "Motif ")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin + 15*mm, y_pos, f"Frais de scolarité {eleve['annee_libelle']}")
        
        c.line(margin, y_pos - 5, width - margin, y_pos - 5)
        
        # f) Ligne basse
        y_pos -= 20 * mm
        
        # Cadre "Montant payé" à gauche
        cadre_width = 60 * mm
        cadre_height = 20 * mm
        c.setStrokeColor(ENCRE)
        c.setLineWidth(1)
        c.setFillColor(PAPIER)
        c.rect(margin, y_pos - cadre_height, cadre_width, cadre_height, fill=True, stroke=True)
        
        c.setFont("Helvetica", 10)
        c.setFillColor(ENCRE)
        c.drawString(margin + 5*mm, y_pos - 5*mm, "Montant payé")
        
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(VERT)
        montant_formate = formater_montant(paiement['montant'])
        c.drawString(margin + 5*mm, y_pos - 15*mm, montant_formate)
        
        # Trois lignes à droite
        lines_x = margin + cadre_width + 20 * mm
        lines_y = y_pos
        
        c.setFont("Helvetica", 10)
        c.setFillColor(ENCRE)
        
        c.drawString(lines_x, lines_y - 5, f"Total dû")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(lines_x + 30*mm, lines_y - 5, formater_montant(total_du))
        
        c.setFont("Helvetica", 10)
        c.drawString(lines_x, lines_y - 10, f"Déjà versé (avec ce paiement)")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(lines_x + 30*mm, lines_y - 10, formater_montant(deja_verse))
        
        # Solde restant avec filet au-dessus
        c.setStrokeColor(ENCRE)
        c.setLineWidth(0.5)
        c.line(lines_x, lines_y - 13, width - margin, lines_y - 13)
        
        c.setFont("Helvetica", 10)
        c.drawString(lines_x, lines_y - 18, f"Solde restant")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(lines_x + 30*mm, lines_y - 18, formater_montant(solde_apres))
        
        # g) Bandeau bas
        band_height = 22 * mm
        band_y = margin
        c.setFillColor(VERT)
        c.setFillAlpha(0.16)
        c.rect(0, band_y, width, band_height, fill=True, stroke=False)
        c.setFillAlpha(1.0)
        
        # Signatures
        c.setFont("Helvetica", 10)
        c.setFillColor(ENCRE)
        
        c.drawString(margin, band_y + 12*mm, "Reçu par (Secrétariat)")
        c.setStrokeColor(ENCRE)
        c.setLineWidth(0.5)
        c.line(margin, band_y + 8*mm, margin + 50*mm, band_y + 8*mm)
        
        signature_x = width - margin - 80*mm
        c.drawString(signature_x, band_y + 12*mm, "Cachet et signature")
        c.line(signature_x, band_y + 8*mm, signature_x + 80*mm, band_y + 8*mm)
        
        # Sauvegarder le PDF
        c.save()
        
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
