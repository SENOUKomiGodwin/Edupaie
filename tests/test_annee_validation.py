"""
Tests pour la validation des années scolaires.
"""

import pytest
from services.annee_service import AnneeService
from datetime import datetime


class TestAnneeValidation:
    """Tests pour la validation du format des années scolaires."""
    
    def test_format_valide(self):
        """Test que les formats valides sont acceptés."""
        formats_valides = [
            "2024-2025",
            "2023-2024",
            "2000-2001",
            f"{datetime.now().year}-{datetime.now().year + 1}",
            f"{datetime.now().year + 5}-{datetime.now().year + 6}",
        ]
        
        for libelle in formats_valides:
            assert AnneeService._valider_format_annee(libelle), f"{libelle} devrait être valide"
    
    def test_format_invalide_mauvais_separateur(self):
        """Test que les séparateurs incorrects sont refusés."""
        formats_invalides = [
            "2024/2025",
            "2024_2025",
            "2024 2025",
            "20242025",
        ]
        
        for libelle in formats_invalides:
            assert not AnneeService._valider_format_annee(libelle), f"{libelle} devrait être invalide"
    
    def test_format_invalide_annee_pas_consecutive(self):
        """Test que les années non consécutives sont refusées."""
        formats_invalides = [
            "2024-2026",
            "2024-2027",
            "2024-2024",
            "2024-2023",
        ]
        
        for libelle in formats_invalides:
            assert not AnneeService._valider_format_annee(libelle), f"{libelle} devrait être invalide"
    
    def test_format_invalide_annee_trop_ancienne(self):
        """Test que les années avant 2000 sont refusées."""
        formats_invalides = [
            "1999-2000",
            "1990-1991",
            "1980-1981",
        ]
        
        for libelle in formats_invalides:
            assert not AnneeService._valider_format_annee(libelle), f"{libelle} devrait être invalide"
    
    def test_format_invalide_annee_tout_futur(self):
        """Test que les années trop dans le futur sont refusées."""
        annee_courante = datetime.now().year
        formats_invalides = [
            f"{annee_courante + 6}-{annee_courante + 7}",
            f"{annee_courante + 10}-{annee_courante + 11}",
            "2099-2100",
        ]
        
        for libelle in formats_invalides:
            assert not AnneeService._valider_format_annee(libelle), f"{libelle} devrait être invalide"
    
    def test_format_invalide_pas_des_chiffres(self):
        """Test que les formats non numériques sont refusés."""
        formats_invalides = [
            "abcd-efgh",
            "aaaa-bbbb",
            "20ab-20cd",
        ]
        
        for libelle in formats_invalides:
            assert not AnneeService._valider_format_annee(libelle), f"{libelle} devrait être invalide"
    
    def test_creer_annee_format_invalide(self):
        """Test que la création d'année invalide lève une erreur."""
        with pytest.raises(ValueError, match="format AAAA-AAAA"):
            AnneeService.creer_annee("2099-2100")
        
        with pytest.raises(ValueError, match="format AAAA-AAAA"):
            AnneeService.creer_annee("2024-2026")
    
    def test_creer_annee_format_valide(self):
        """Test que la création d'année valide fonctionne."""
        annee_id = AnneeService.creer_annee("2026-2027")
        assert annee_id > 0
