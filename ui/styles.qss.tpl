/*
EduPaie — feuille de style (modèle avec marqueurs).

Les marqueurs double-accolades sont remplacés au chargement par les constantes
de ui/theme.py (voir ui/style_loader.py). Le QSS Qt ne supporte ni
variables ni box-shadow ni flexbox : seules les propriétés listées
ci-dessous sont utilisées.
*/

/* ---------- Global ---------- */
QMainWindow, QWidget {
    background-color: {{FOND}};
    color: {{TEXTE}};
    font-family: "{{POLICE}}";
    font-size: {{TAILLE_CORPS}}px;
}

QToolTip {
    background-color: {{TEXTE}};
    color: {{CARTE}};
    border: none;
    padding: 6px 10px;
}

/* ---------- Titres ---------- */
QLabel#pageTitle {
    font-size: {{TAILLE_TITRE_PAGE}}px;
    font-weight: 500;
    color: {{TEXTE}};
}

QLabel#pageSubtitle {
    font-size: {{TAILLE_CORPS}}px;
    color: {{TEXTE_SECOND}};
}

QLabel#sectionTitle {
    font-size: {{TAILLE_CORPS}}px;
    font-weight: 500;
    color: {{TEXTE}};
}

QLabel#legendLabel {
    font-size: {{TAILLE_LEGENDE}}px;
    color: {{TEXTE_DISCRET}};
}

/* ---------- Cartes ---------- */
QFrame#card {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CARTE}}px;
}

QFrame#sidebar {
    background-color: {{CARTE}};
    border-right: 1px solid {{BORDURE}};
}

/* ---------- Champs de saisie ---------- */
QLineEdit, QComboBox, QSpinBox, QDateEdit {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE_CHAMP}};
    border-radius: {{RAYON_CONTROLE}}px;
    padding: 6px 10px;
    color: {{TEXTE}};
    selection-background-color: {{VERT}};
    selection-color: {{CARTE}};
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
    border: 1px solid {{VERT}};
}

QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDateEdit:disabled {
    background-color: {{FOND}};
    color: {{TEXTE_DISCRET}};
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QComboBox QAbstractItemView {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CONTROLE}}px;
    selection-background-color: {{VERT_FOND}};
    selection-color: {{TEXTE}};
    outline: none;
}

QDateEdit::drop-down {
    border: none;
    width: 22px;
}

/* ---------- Boutons ---------- */
QPushButton {
    background-color: {{CARTE}};
    color: {{TEXTE_SECOND}};
    border: 1px solid {{BORDURE_CHAMP}};
    border-radius: {{RAYON_CONTROLE}}px;
    padding: 7px 12px;
    font-weight: 400;
}

QPushButton:hover {
    background-color: {{SEPARATEUR}};
}

QPushButton:pressed {
    background-color: {{BORDURE}};
}

QPushButton:disabled {
    color: {{TEXTE_DISCRET}};
    background-color: {{FOND}};
    border-color: {{BORDURE}};
}

QPushButton:focus {
    border: 1px solid {{VERT}};
}

/* Action principale : un seul bouton plein vert par zone */
QPushButton[variant="primary"] {
    background-color: {{VERT}};
    color: {{CARTE}};
    border: 1px solid {{VERT}};
    font-weight: 500;
}

QPushButton[variant="primary"]:hover {
    background-color: {{VERT_HOVER}};
    border-color: {{VERT_HOVER}};
}

QPushButton[variant="primary"]:pressed {
    background-color: {{VERT_HOVER}};
}

QPushButton[variant="primary"]:disabled {
    background-color: {{VERT_FOND}};
    color: {{TEXTE_DISCRET}};
    border-color: {{VERT_FOND}};
}

/* Action destructive : texte rouge, bordure rouge clair */
QPushButton[variant="danger"] {
    background-color: {{CARTE}};
    color: {{ROUGE}};
    border: 1px solid {{ROUGE_BORDURE}};
}

QPushButton[variant="danger"]:hover {
    background-color: {{ROUGE_FOND}};
}

QPushButton[variant="danger"]:pressed {
    background-color: {{ROUGE_BORDURE}};
}

/* ---------- Tableaux ---------- */
QTableView, QTableWidget {
    background-color: {{CARTE}};
    alternate-background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CARTE}}px;
    gridline-color: {{SEPARATEUR}};
    selection-background-color: {{VERT_FOND}};
    selection-color: {{TEXTE}};
    outline: none;
}

QTableView::item, QTableWidget::item {
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid {{SEPARATEUR}};
}

QHeaderView::section {
    background-color: {{FOND}};
    color: {{TEXTE_SECOND}};
    font-size: {{TAILLE_LEGENDE}}px;
    font-weight: 500;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {{BORDURE}};
}

/* ---------- Barres de défilement ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: {{BORDURE_CHAMP}};
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: {{TEXTE_DISCRET}};
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: {{BORDURE_CHAMP}};
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: {{TEXTE_DISCRET}};
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
}

QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}
