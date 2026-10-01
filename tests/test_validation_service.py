"""
Tests unitaires pour le service de validation.
"""

import pytest
from datetime import datetime, date, timedelta
from services.validation_service import ValidationService, ValidationError


class TestValidationDate:
    """Tests pour la validation des dates."""

    def test_date_valide(self):
        """Teste une date valide."""
        assert ValidationService.valider_date("30/09/2026") == "30/09/2026"
        assert ValidationService.valider_date("01/01/2025") == "01/01/2025"

    def test_date_avec_espaces(self):
        """Teste une date avec des espaces."""
        assert ValidationService.valider_date(" 30/09/2026 ") == "30/09/2026"

    def test_date_vide(self):
        """Teste qu'une date vide est refusée."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_date("")
        assert "obligatoire" in str(exc.value).lower()

    def test_date_inexistante(self):
        """Teste une date inexistante (31/02/2026)."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_date("31/02/2026")
        assert "format" in str(exc.value).lower()

    def test_date_format_invalide(self):
        """Teste un format invalide."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_date("2026-09-30")
        assert "format" in str(exc.value).lower()

    def test_date_future(self):
        """Teste qu'une date future est refusée."""
        future = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_date(future)
        assert "futur" in str(exc.value).lower()

    def test_date_aujourdhui(self):
        """Teste que la date d'aujourd'hui est acceptée."""
        today = datetime.now().strftime("%d/%m/%Y")
        assert ValidationService.valider_date(today) == today


class TestValidationMontant:
    """Tests pour la validation des montants."""

    def test_montant_valide(self):
        """Teste un montant valide."""
        assert ValidationService.valider_montant("25 000") == 25000
        assert ValidationService.valider_montant("25000") == 25000

    def test_montant_avec_fcfa(self):
        """Teste un montant avec FCFA."""
        assert ValidationService.valider_montant("25 000 FCFA") == 25000
        assert ValidationService.valider_montant("1 FCFA") == 1

    def test_montant_avec_espaces_speciaux(self):
        """Teste un montant avec espaces spéciaux."""
        assert ValidationService.valider_montant("25\u00a0000") == 25000
        assert ValidationService.valider_montant("25\u202f000") == 25000

    def test_montant_lettres_refuse(self):
        """Teste que les lettres sont refusées."""
        with pytest.raises(ValidationError):
            ValidationService.valider_montant("abc")

    def test_montant_decimales_refuse(self):
        """Teste que les décimales sont refusées."""
        with pytest.raises(ValidationError):
            ValidationService.valider_montant("12,5")

    def test_montant_zero_refuse(self):
        """Teste que zéro est refusé."""
        with pytest.raises(ValidationError):
            ValidationService.valider_montant("0")

    def test_montant_negatif_refuse(self):
        """Teste que les négatifs sont refusés."""
        with pytest.raises(ValidationError):
            ValidationService.valider_montant("-5")

    def test_montant_entier_negatif_refuse(self):
        """Teste qu'un montant entier négatif est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_montant_entier(-1000)
        assert "négatif" in str(exc.value).lower()

    def test_montant_entier_valide(self):
        """Teste un montant entier valide."""
        assert ValidationService.valider_montant_entier(25000) == 25000
        assert ValidationService.valider_montant_entier(1) == 1

    def test_montant_entier_avec_fcfa(self):
        """Teste que valider_montant_entier accepte les chaînes avec FCFA."""
        assert ValidationService.valider_montant_entier("20000 FCFA") == 20000
        assert ValidationService.valider_montant_entier("25 000 FCFA") == 25000
        assert ValidationService.valider_montant_entier("1 FCFA") == 1

    def test_montant_entier_type_invalide(self):
        """Teste que valider_montant_entier refuse les types invalides."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_montant_entier(None)
        assert "entier" in str(exc.value).lower()

        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_montant_entier(3.14)
        assert "entier" in str(exc.value).lower()


class TestValidationNom:
    """Tests pour la validation des noms."""

    def test_nom_valide(self):
        """Teste un nom valide."""
        assert ValidationService.valider_nom("Koffi") == "Koffi"
        assert ValidationService.valider_nom("Yawovi") == "Yawovi"

    def test_nom_avec_espaces(self):
        """Teste un nom avec des espaces."""
        assert ValidationService.valider_nom("  Koffi  ") == "Koffi"

    def test_nom_vide(self):
        """Teste qu'un nom vide est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_nom("")
        assert "obligatoire" in str(exc.value).lower()

    def test_nom_trop_court(self):
        """Teste qu'un nom trop court est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_nom("A")
        assert "2 caractères" in str(exc.value)

    def test_nom_trop_long(self):
        """Teste qu'un nom trop long est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_nom("A" * 101)
        assert "100 caractères" in str(exc.value)


class TestValidationModePaiement:
    """Tests pour la validation des modes de paiement."""

    def test_mode_valide(self):
        """Teste un mode de paiement valide."""
        assert ValidationService.valider_mode_paiement("especes") == "especes"
        assert ValidationService.valider_mode_paiement("cheque") == "cheque"
        assert ValidationService.valider_mode_paiement("virement") == "virement"
        assert ValidationService.valider_mode_paiement("mobile_money") == "mobile_money"

    def test_mode_invalide(self):
        """Teste qu'un mode invalide est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_mode_paiement("paypal")
        assert "invalide" in str(exc.value).lower()


class TestValidationID:
    """Tests pour la validation des IDs."""

    def test_id_valide(self):
        """Teste un ID valide."""
        assert ValidationService.valider_id(1) == 1
        assert ValidationService.valider_id(100) == 100

    def test_id_zero_refuse(self):
        """Teste que zéro est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_id(0)
        assert "positif" in str(exc.value).lower()

    def test_id_negatif_refuse(self):
        """Teste qu'un ID négatif est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_id(-1)
        assert "positif" in str(exc.value).lower()

    def test_id_none_refuse(self):
        """Teste que None est refusé."""
        with pytest.raises(ValidationError) as exc:
            ValidationService.valider_id(None)
        assert "positif" in str(exc.value).lower()
