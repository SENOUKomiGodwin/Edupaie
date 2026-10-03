"""
Tests pour le service de génération de reçus PDF.
"""

import pytest
import os
from pathlib import Path
from services.recu_service import RecuService
from data.repositories.paiement_repository import PaiementRepository
from data.repositories.eleve_repository import EleveRepository
from data.repositories.classe_repository import ClasseRepository
from data.repositories.annee_repository import AnneeRepository


class TestRecuService:
    """Tests pour RecuService."""
    
    @pytest.fixture(scope="function")
    def setup_paiement(self):
        """Crée un paiement de test."""
        import random
        import time
        
        # Créer une classe avec un nom unique
        classe_id = ClasseRepository.create(f"TestClasse_{random.randint(1000, 9999)}")
        
        # Créer une année avec un libellé unique
        annee_id = AnneeRepository.create(f"2100-2101_{int(time.time() * 1000)}")
        
        # Créer un élève
        eleve_id = EleveRepository.create(
            "Test", "Élève", classe_id, annee_id, 250000
        )
        
        # Créer un paiement
        paiement_id = PaiementRepository.create(
            eleve_id, 25000, "02/10/2026", "especes", 
            f"REC-2100-{int(time.time() * 1000)}", 225000
        )
        
        return paiement_id, eleve_id
    
    def test_generation_pdf_sans_exception(self, setup_paiement):
        """Test que le PDF est généré sans exception."""
        paiement_id, _ = setup_paiement
        
        pdf_path = RecuService.generer_pdf(paiement_id)
        
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')
        
        # Nettoyer
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_pdf_une_seule_page(self, setup_paiement):
        """Test que le PDF fait exactement 1 page."""
        paiement_id, _ = setup_paiement
        
        pdf_path = RecuService.generer_pdf(paiement_id)
        
        # Lire le PDF et vérifier le nombre de pages
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        assert len(reader.pages) == 1
        
        # Nettoyer
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_contenu_pdf(self, setup_paiement):
        """Test que le texte extrait contient les informations attendues."""
        paiement_id, _ = setup_paiement
        
        pdf_path = RecuService.generer_pdf(paiement_id)
        
        # Extraire le texte du PDF
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        assert "Test Élève" in text
        assert "FCFA" in text
        assert "vingt-cinq mille" in text.lower()
        
        # Nettoyer
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_nom_tres_long(self, setup_paiement):
        """Test avec un nom d'élève très long."""
        paiement_id, eleve_id = setup_paiement
        
        # Modifier l'élève avec un nom très long
        EleveRepository.update(
            eleve_id, 
            "NomTresLongQuiPourraitDeborderSilNestPasCoupeCorrectement", 
            "PrenomTresLongAussi", 
            1, 1, 250000
        )
        
        pdf_path = RecuService.generer_pdf(paiement_id)
        
        assert os.path.exists(pdf_path)
        
        # Nettoyer
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_montant_gros(self, setup_paiement):
        """Test avec un montant de 1 000 000 FCFA."""
        paiement_id, eleve_id = setup_paiement
        
        # Modifier le paiement avec un gros montant
        PaiementRepository.create(
            eleve_id, 1000000, "02/10/2026", "especes",
            "REC-2026-000043", 0
        )
        
        pdf_path = RecuService.generer_pdf(paiement_id + 1)
        
        assert os.path.exists(pdf_path)
        
        # Nettoyer
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_modes_paiement(self, setup_paiement):
        """Test chaque mode de paiement."""
        paiement_id, eleve_id = setup_paiement
        import time
        
        modes = ["especes", "cheque", "virement", "mobile_money"]
        
        for i, mode in enumerate(modes):
            PaiementRepository.create(
                eleve_id, 25000, "02/10/2026", mode,
                f"REC-2101-{int(time.time())}{i}", 225000
            )
            pdf_path = RecuService.generer_pdf(paiement_id + i + 1)
            assert os.path.exists(pdf_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    def test_idempotence(self, setup_paiement):
        """Test que deux générations successives donnent le même contenu."""
        paiement_id, _ = setup_paiement
        
        pdf_path1 = RecuService.generer_pdf(paiement_id)
        pdf_path2 = RecuService.generer_pdf(paiement_id)
        
        # Comparer les fichiers
        from PyPDF2 import PdfReader
        reader1 = PdfReader(pdf_path1)
        reader2 = PdfReader(pdf_path2)
        
        text1 = ""
        text2 = ""
        for page in reader1.pages:
            text1 += page.extract_text()
        for page in reader2.pages:
            text2 += page.extract_text()
        
        assert text1 == text2
        
        # Nettoyer
        if os.path.exists(pdf_path1):
            os.remove(pdf_path1)
        if os.path.exists(pdf_path2):
            os.remove(pdf_path2)
