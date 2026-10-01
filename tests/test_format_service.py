"""
Tests unitaires pour le service de formatage.
"""

import pytest
from datetime import datetime, date
from services.format_service import formater_montant, parser_montant, montant_en_lettres, parser_date


class TestFormatMontant:
    """Tests pour la fonction formater_montant."""
    
    def test_montant_simple(self):
        """Teste le formatage d'un montant simple."""
        assert formater_montant(25000) == "25 000 FCFA"
    
    def test_montant_million(self):
        """Teste le formatage d'un montant en millions."""
        assert formater_montant(1500000) == "1 500 000 FCFA"
    
    def test_montant_zero(self):
        """Teste le formatage de zéro."""
        assert formater_montant(0) == "0 FCFA"
    
    def test_montant_negatif(self):
        """Teste que les montants négatifs lèvent une erreur."""
        with pytest.raises(ValueError):
            formater_montant(-1000)


class TestParserMontant:
    """Tests pour la fonction parser_montant."""
    
    def test_parser_simple(self):
        """Teste le parsing d'un montant simple."""
        assert parser_montant("25000") == 25000
    
    def test_parser_avec_espaces(self):
        """Teste le parsing avec espaces."""
        assert parser_montant("25 000") == 25000
        assert parser_montant("1 500 000") == 1500000
    
    def test_parser_lettres_refuse(self):
        """Teste que les lettres sont refusées."""
        with pytest.raises(ValueError):
            parser_montant("abc")
    
    def test_parser_decimales_refuse(self):
        """Teste que les décimales sont refusées."""
        with pytest.raises(ValueError):
            parser_montant("25.5")
    
    def test_parser_zero_refuse(self):
        """Teste que zéro est refusé."""
        with pytest.raises(ValueError):
            parser_montant("0")
    
    def test_parser_negatif_refuse(self):
        """Teste que les négatifs sont refusés."""
        with pytest.raises(ValueError):
            parser_montant("-1000")

    def test_parser_avec_fcfa(self):
        """Teste que 'FCFA' est retiré."""
        assert parser_montant("25 000 FCFA") == 25000
        assert parser_montant("25000FCFA") == 25000
        assert parser_montant("25 000 fcfa") == 25000

    def test_parser_avec_espaces_speciaux(self):
        """Teste que les espaces spéciaux sont acceptés."""
        assert parser_montant("25\u00a0000") == 25000  # Espace insécable
        assert parser_montant("25\u202f000") == 25000  # Espace fine insécable

    def test_parser_1_fcfa(self):
        """Teste le cas '1 FCFA' du bug."""
        assert parser_montant("1 FCFA") == 1
        assert parser_montant("1") == 1


class TestMontantEnLettres:
    """Tests pour la fonction montant_en_lettres."""
    
    def test_zero(self):
        """Teste zéro."""
        assert montant_en_lettres(0) == "Zéro francs CFA"
    
    def test_unite(self):
        """Teste les unités."""
        assert montant_en_lettres(1) == "Un franc CFA"
        assert montant_en_lettres(5).lower() == "cinq francs cfa"
    
    def test_dizaine(self):
        """Teste les dizaines."""
        assert montant_en_lettres(10).lower() == "dix francs cfa"
        assert montant_en_lettres(20).lower() == "vingt francs cfa"
        assert montant_en_lettres(50).lower() == "cinquante francs cfa"
    
    def test_centaine(self):
        """Teste les centaines."""
        assert montant_en_lettres(100).lower() == "cent francs cfa"
        assert montant_en_lettres(200).lower() == "deux cents francs cfa"
    
    def test_millier(self):
        """Teste les milliers."""
        assert montant_en_lettres(1000).lower() == "mille francs cfa"
        assert montant_en_lettres(2000).lower() == "deux mille francs cfa"
    
    def test_cas_speciaux_11_19(self):
        """Teste les cas spéciaux 11-19."""
        assert "onze" in montant_en_lettres(11)
        assert "douze" in montant_en_lettres(12)
        assert "dix-neuf" in montant_en_lettres(19)
    
    def test_complex(self):
        """Teste un montant complexe."""
        assert "vingt-cinq" in montant_en_lettres(25000)
        assert "mille" in montant_en_lettres(25000)
    
    def test_negatif_refuse(self):
        """Teste que les négatifs sont refusés."""
        with pytest.raises(ValueError):
            montant_en_lettres(-1000)


class TestParserDate:
    """Tests pour la fonction parser_date."""

    def test_date_str_valide(self):
        """Teste une date valide en chaîne."""
        assert parser_date("30/09/2026") == "30/09/2026"
        assert parser_date("01/01/2025") == "01/01/2025"

    def test_date_objet_date(self):
        """Teste avec un objet date."""
        d = date(2026, 9, 30)
        assert parser_date(d) == "30/09/2026"

    def test_date_objet_datetime(self):
        """Teste avec un objet datetime."""
        dt = datetime(2026, 9, 30, 14, 30)
        assert parser_date(dt) == "30/09/2026"

    def test_date_avec_espaces(self):
        """Teste avec des espaces parasites."""
        assert parser_date(" 30/09/2026 ") == "30/09/2026"
        assert parser_date("  30/09/2026  ") == "30/09/2026"

    def test_date_inexistante(self):
        """Teste une date inexistante (31/02/2026)."""
        with pytest.raises(ValueError):
            parser_date("31/02/2026")

    def test_date_format_invalide(self):
        """Teste un format invalide."""
        with pytest.raises(ValueError):
            parser_date("2026-09-30")
        with pytest.raises(ValueError):
            parser_date("30-09-2026")

    def test_date_type_invalide(self):
        """Teste un type invalide."""
        with pytest.raises(ValueError):
            parser_date(12345)
        with pytest.raises(ValueError):
            parser_date(None)
