"""
Service de validation centralisée.

Contient les fonctions de validation pour tous les champs de l'application.
"""

from typing import Optional, Union
from services.format_service import parser_montant, parser_date


class ValidationError(Exception):
    """Exception levée lors d'une erreur de validation."""
    pass


class ValidationService:
    """Service pour la validation des données."""
    
    @staticmethod
    def valider_nom(nom: str, champ: str = "Nom") -> str:
        """
        Valide un nom ou prénom.
        
        Args:
            nom: Le nom à valider
            champ: Nom du champ pour le message d'erreur
            
        Returns:
            Le nom nettoyé (strip)
            
        Raises:
            ValidationError: Si le nom est invalide
        """
        if not nom or not nom.strip():
            raise ValidationError(f"Le {champ.lower()} est obligatoire")
        
        nom_nettoye = nom.strip()
        
        if len(nom_nettoye) < 2:
            raise ValidationError(f"Le {champ.lower()} doit contenir au moins 2 caractères")
        
        if len(nom_nettoye) > 100:
            raise ValidationError(f"Le {champ.lower()} ne peut pas dépasser 100 caractères")
        
        return nom_nettoye
    
    @staticmethod
    def valider_montant(montant_texte: str, champ: str = "Montant") -> int:
        """
        Valide un montant en FCFA.
        
        Args:
            montant_texte: Le montant sous forme de texte
            champ: Nom du champ pour le message d'erreur
            
        Returns:
            Le montant en entier
            
        Raises:
            ValidationError: Si le montant est invalide
        """
        try:
            montant = parser_montant(montant_texte)
            
            if montant < 0:
                raise ValidationError(f"Le {champ.lower()} ne peut pas être négatif")
            
            if montant > 999999999:
                raise ValidationError(f"Le {champ.lower()} ne peut pas dépasser 999 999 999 FCFA")
            
            return montant
            
        except ValueError as e:
            raise ValidationError(str(e))
    
    @staticmethod
    def valider_montant_entier(montant: Union[int, str], champ: str = "Montant") -> int:
        """
        Valide un montant en FCFA (entier ou chaîne).

        Accepte les entiers ou les chaînes avec FCFA, espaces, etc.
        Utilise parser_montant si le montant est une chaîne.

        Args:
            montant: Le montant (int ou str, ex: 20000 ou "20000 FCFA")
            champ: Nom du champ pour le message d'erreur

        Returns:
            Le montant validé (entier)

        Raises:
            ValidationError: Si le montant est invalide
        """
        # Si c'est une chaîne, utiliser parser_montant
        if isinstance(montant, str):
            montant = parser_montant(montant)

        # Maintenant montant doit être un entier
        if not isinstance(montant, int):
            raise ValidationError(f"Le {champ.lower()} doit être un nombre entier")

        if montant < 0:
            raise ValidationError(f"Le {champ.lower()} ne peut pas être négatif")

        if montant > 999999999:
            raise ValidationError(f"Le {champ.lower()} ne peut pas dépasser 999 999 999 FCFA")

        return montant
    
    @staticmethod
    def valider_date(date_str: str, champ: str = "Date") -> str:
        """
        Valide une date au format JJ/MM/AAAA.

        Args:
            date_str: La date sous forme de texte
            champ: Nom du champ pour le message d'erreur

        Returns:
            La date validée

        Raises:
            ValidationError: Si la date est invalide ou dans le futur
        """
        from datetime import datetime
        from config import FORMAT_DATE

        if not date_str or not date_str.strip():
            raise ValidationError(f"La {champ.lower()} est obligatoire")

        try:
            date_formatee = parser_date(date_str)
            date_obj = datetime.strptime(date_formatee, FORMAT_DATE)

            # Vérifier que la date n'est pas dans le futur
            date_actuelle = datetime.now()
            if date_obj > date_actuelle:
                raise ValidationError(f"La {champ.lower()} ne peut pas être dans le futur")

            return date_formatee

        except ValueError as e:
            # Messages d'erreur séparés
            msg = str(e)
            if "format" in msg.lower():
                raise ValidationError(f"La {champ.lower()} doit être au format JJ/MM/AAAA")
            else:
                raise ValidationError(f"La {champ.lower()} est invalide : {msg}")
    
    @staticmethod
    def valider_mode_paiement(mode: str) -> str:
        """
        Valide un mode de paiement.
        
        Args:
            mode: Le mode de paiement
            
        Returns:
            Le mode validé
            
        Raises:
            ValidationError: Si le mode est invalide
        """
        from config import MODES_PAIEMENT
        
        if not mode or mode not in MODES_PAIEMENT:
            modes_autorises = ", ".join(MODES_PAIEMENT.values())
            raise ValidationError(
                f"Mode de paiement invalide. Modes autorisés : {modes_autorises}"
            )
        
        return mode
    
    @staticmethod
    def valider_id(id_value: int, champ: str = "ID") -> int:
        """
        Valide un ID (doit être positif).
        
        Args:
            id_value: L'ID à valider
            champ: Nom du champ pour le message d'erreur
            
        Returns:
            L'ID validé
            
        Raises:
            ValidationError: Si l'ID est invalide
        """
        if id_value is None or id_value <= 0:
            raise ValidationError(f"Le {champ.lower()} doit être un entier positif")
        
        return id_value
