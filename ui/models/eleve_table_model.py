"""
Modèle de table Qt pour la liste des élèves.

Adapte les données des élèves pour l'affichage dans un QTableView avec tri.
"""

from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QColor
from typing import List, Dict
from config import STATUT_SOLDE, STATUT_PARTIEL, STATUT_NON_PAYE


class EleveTableModel(QAbstractTableModel):
    """Modèle de table pour les élèves."""

    def __init__(self, data: List[Dict] = None):
        super().__init__()
        self._data = data or []
        self._headers = ["Élève", "Classe", "Total dû", "Solde", "Statut"]

    def rowCount(self, parent=None):
        """Retourne le nombre de lignes."""
        return len(self._data)

    def columnCount(self, parent=None):
        """Retourne le nombre de colonnes."""
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        """Retourne les données pour une cellule."""
        if not index.isValid():
            return None

        eleve = self._data[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:  # Élève
                nom = eleve.get("nom", "")
                prenom = eleve.get("prenom", "")
                return f"{nom} {prenom}"
            elif col == 1:  # Classe
                return eleve.get("classe_nom", "")
            elif col == 2:  # Total dû
                return eleve.get("total_formate", str(eleve.get("montant_total_du", 0)))
            elif col == 3:  # Solde
                return eleve.get("solde_formate", str(eleve.get("solde", 0)))
            elif col == 4:  # Statut
                return eleve.get("statut", "")

        elif role == Qt.ForegroundRole and col == 4:
            # Code couleur pour le statut (texte coloré)
            statut = eleve.get("statut", "")
            if statut == STATUT_SOLDE:
                return QColor(4, 120, 87)  # #047857
            elif statut == STATUT_PARTIEL:
                return QColor(180, 83, 9)  # #B45309
            elif statut == STATUT_NON_PAYE:
                return QColor(185, 28, 28)  # #B91C1C

        elif role == Qt.TextAlignmentRole:
            if col in [2, 3]:  # Montants alignés à droite
                return Qt.AlignRight | Qt.AlignVCenter
            else:  # Texte aligné à gauche
                return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Retourne les en-têtes de colonnes."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def set_data(self, data: List[Dict]):
        """
        Met à jour les données du modèle.

        Args:
            data: Nouvelle liste d'élèves
        """
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def get_eleve_id(self, index):
        """
        Retourne l'ID de l'élève à l'index donné (utilise l'index source).

        Args:
            index: Index de la ligne dans le modèle source

        Returns:
            ID de l'élève
        """
        if 0 <= index < len(self._data):
            return self._data[index].get("id")
        return None
