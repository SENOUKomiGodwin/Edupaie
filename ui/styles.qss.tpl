/*
EduPaie — feuille de style QSS moderne avec marqueurs dynamiques.
Substitué au chargement par les constantes de ui/theme.py.
*/

/* ---------- Base globale ---------- */
QMainWindow {
    background-color: {{FOND}};
}

QWidget {
    color: {{TEXTE}};
    font-family: {{POLICE}};
    font-size: {{TAILLE_CORPS}}px;
}

QToolTip {
    background-color: {{TEXTE}};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ---------- Typographie et en-têtes ---------- */
QLabel#pageTitle {
    font-size: {{TAILLE_TITRE_PAGE}}px;
    font-weight: 600;
    color: {{TEXTE}};
    background: transparent;
}

QLabel#pageSubtitle {
    font-size: {{TAILLE_SOUS_TITRE}}px;
    color: {{TEXTE_SECOND}};
    background: transparent;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: {{TEXTE}};
    background: transparent;
}

QLabel#legendLabel {
    font-size: {{TAILLE_LEGENDE}}px;
    color: {{TEXTE_DISCRET}};
    background: transparent;
}

QLabel#statLabel {
    font-size: 13px;
    color: {{TEXTE_SECOND}};
    background: transparent;
}

QLabel#statValue {
    font-size: {{TAILLE_STAT}}px;
    font-weight: 700;
    background: transparent;
}

/* ---------- Cartes et conteneurs ---------- */
QFrame#card {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CARTE}}px;
}

QFrame#sidebar {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_SIDEBAR}}px;
}

QFrame#statCard {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CARTE}}px;
}

QFrame#actionBar {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CARTE}}px;
}

/* ---------- Sidebar : Identité & Année ---------- */
QLabel#appName {
    font-size: 16px;
    font-weight: 700;
    color: {{TEXTE}};
    background: transparent;
}

QLabel#appSubtitle {
    font-size: 12px;
    color: {{TEXTE_SECOND}};
    background: transparent;
}

QFrame#yearSelector {
    background-color: {{FOND}};
    border: 1px solid {{BORDURE}};
    border-radius: 10px;
}

QLabel#yearLabel {
    font-size: 11px;
    color: {{TEXTE_SECOND}};
    background: transparent;
}

QLabel#yearValue {
    font-size: 13px;
    font-weight: 600;
    color: {{TEXTE}};
    background: transparent;
}

QComboBox#yearCombo {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE_CHAMP}};
    border-radius: 8px;
    padding: 6px 10px;
    color: {{TEXTE}};
    font-size: 13px;
    font-weight: 500;
    combobox-popup: 0;
}

QComboBox#yearCombo:focus {
    border: 1px solid {{VERT}};
}

QComboBox#yearCombo::drop-down {
    border: none;
    width: 20px;
}

QComboBox#yearCombo QAbstractItemView {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: 8px;
    selection-background-color: {{VERT_FOND}};
    selection-color: {{TEXTE}};
    padding: 4px;
    outline: none;
}

QPushButton#newYearBtn {
    background-color: transparent;
    color: {{VERT}};
    border: 1px dashed {{VERT}};
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 10px;
}

QPushButton#newYearBtn:hover {
    background-color: {{VERT_FOND}};
}

QLabel#menuLabel {
    font-size: 11px;
    font-weight: 600;
    color: {{TEXTE_DISCRET}};
    letter-spacing: 1px;
    background: transparent;
}

/* ---------- Sidebar : Navigation ---------- */
QPushButton#navItem {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    color: {{TEXTE_SECOND}};
    font-size: 13px;
    font-weight: 400;
}

QPushButton#navItem:hover {
    background-color: {{SEPARATEUR}};
    color: {{TEXTE}};
}

QPushButton#navItemActive {
    background-color: {{VERT_FOND}};
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    color: {{VERT_TEXTE}};
    font-size: 13px;
    font-weight: 600;
}

QLabel#navBadge {
    background-color: {{VERT_CLAIR}};
    color: {{VERT_TEXTE}};
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#navBadgeInactive {
    background-color: {{SEPARATEUR}};
    color: {{TEXTE_SECOND}};
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 500;
}

QFrame#userSection {
    background: transparent;
    border: none;
    border-top: 1px solid {{BORDURE}};
}

QLabel#userAvatar {
    background-color: {{SEPARATEUR}};
    border-radius: 16px;
    color: {{TEXTE_SECOND}};
    font-weight: 600;
    font-size: 12px;
}

QLabel#userName {
    font-size: 13px;
    font-weight: 600;
    color: {{TEXTE}};
    background: transparent;
}

QLabel#userRole {
    font-size: 11px;
    color: {{TEXTE_DISCRET}};
    background: transparent;
}

/* ---------- Champs de saisie ---------- */
QLineEdit, QComboBox, QSpinBox, QDateEdit {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE_CHAMP}};
    border-radius: 10px;
    padding: 8px 12px;
    color: {{TEXTE}};
    selection-background-color: {{VERT}};
    selection-color: #FFFFFF;
    min-height: 20px;
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
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: 8px;
    selection-background-color: {{VERT_FOND}};
    selection-color: {{TEXTE}};
    padding: 4px;
    outline: none;
}

QDateEdit::drop-down {
    border: none;
    width: 24px;
}

/* ---------- Boutons standards ---------- */
QPushButton {
    background-color: {{CARTE}};
    color: {{TEXTE_SECOND}};
    border: 1px solid {{BORDURE_CHAMP}};
    border-radius: {{RAYON_CONTROLE}}px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: {{SEPARATEUR}};
    border-color: {{BORDURE_CHAMP}};
    color: {{TEXTE}};
}

QPushButton:pressed {
    background-color: {{BORDURE}};
}

QPushButton:disabled {
    color: {{TEXTE_DISCRET}};
    background-color: {{FOND}};
    border-color: {{BORDURE}};
}

/* Bouton primaire émeraude plein */
QPushButton[variant="primary"] {
    background-color: {{VERT}};
    color: #FFFFFF;
    border: 1px solid {{VERT}};
    font-weight: 600;
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

/* Bouton action destructrice / danger */
QPushButton[variant="danger"] {
    background-color: {{CARTE}};
    color: {{ROUGE}};
    border: 1px solid {{ROUGE_BORDURE}};
}

QPushButton[variant="danger"]:hover {
    background-color: {{ROUGE_FOND}};
}

QPushButton#dangerOutlineBtn {
    background-color: {{CARTE}};
    color: {{ROUGE}};
    border: 1px solid {{ROUGE_BORDURE}};
    border-radius: 8px;
}

QPushButton#dangerOutlineBtn:hover {
    background-color: {{ROUGE_FOND}};
}

/* ---------- Pilules / Chips de filtre ---------- */
QPushButton#filterChip {
    background-color: {{CARTE}};
    color: {{TEXTE_SECOND}};
    border: 1px solid {{BORDURE_CHAMP}};
    border-radius: {{RAYON_PILULE}}px;
    padding: 6px 16px;
    font-weight: 400;
    font-size: 13px;
    min-height: 18px;
}

QPushButton#filterChip:hover {
    background-color: {{SEPARATEUR}};
    color: {{TEXTE}};
}

QPushButton#filterChipActive {
    background-color: {{VERT}};
    color: #FFFFFF;
    border: 1px solid {{VERT}};
    border-radius: {{RAYON_PILULE}}px;
    padding: 6px 16px;
    font-weight: 600;
    font-size: 13px;
    min-height: 18px;
}

/* ---------- Barres de progression ---------- */
QProgressBar {
    border: none;
    border-radius: 2px;
    max-height: 5px;
    min-height: 5px;
    background-color: {{SEPARATEUR}};
}

QProgressBar::chunk {
    border-radius: 2px;
}

QProgressBar#progressGreen::chunk {
    background-color: {{VERT}};
}

QProgressBar#progressOrange::chunk {
    background-color: {{ORANGE}};
}

QProgressBar#progressBlue::chunk {
    background-color: {{BLEU}};
}

/* ---------- Tableaux ---------- */
QTableView, QTableWidget {
    background-color: {{CARTE}};
    alternate-background-color: {{CARTE}};
    border: none;
    gridline-color: transparent;
    selection-background-color: {{VERT_FOND}};
    selection-color: {{TEXTE}};
    outline: none;
}

QTableView::item, QTableWidget::item {
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    min-height: 48px;
}

QTableView::item:selected, QTableWidget::item:selected {
    background-color: {{VERT_FOND}};
    color: {{TEXTE}};
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

QHeaderView::section {
    background-color: {{CARTE}};
    color: {{TEXTE_SECOND}};
    font-size: 12px;
    font-weight: 500;
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid {{BORDURE}};
    text-align: left;
}

/* Padding spécifique pour le tableau des paiements */
QTableWidget#paiementsTable::item {
    padding: 10px 16px;
}

/* ---------- Barres de défilement discrètes ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: {{BORDURE_CHAMP}};
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: {{TEXTE_DISCRET}};
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: {{BORDURE_CHAMP}};
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar:horizontal:hover {
    background: {{TEXTE_DISCRET}};
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
}

QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}

/* ---------- Boîtes de dialogue ---------- */
QDialog {
    background-color: {{FOND}};
}

QDialog QFrame#card {
    background-color: {{CARTE}};
    border: 1px solid {{BORDURE}};
    border-radius: {{RAYON_CARTE}}px;
}

QMessageBox {
    background-color: {{CARTE}};
}

QMessageBox QPushButton {
    min-width: 80px;
}