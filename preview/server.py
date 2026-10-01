"""
Aperçu web local d'EduPaie (lecture seule).

Petit serveur HTTP (stdlib uniquement, aucune dépendance) qui expose les
données réelles de edupaie.db à travers la page preview/index.html.

Usage :
    python preview/server.py [port]   # port par défaut : 8765

La base est ouverte en lecture seule (URI mode=ro) pour ne jamais interférer
avec l'application desktop.
"""

import json
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "edupaie.db"
INDEX_PATH = Path(__file__).with_name("index.html")
DEFAULT_PORT = 8765

MODES_PAIEMENT = {
    "especes": "Espèces",
    "cheque": "Chèque",
    "virement": "Virement",
    "mobile_money": "Mobile money",
}


def fetch_snapshot():
    """Retourne un instantané JSON-compatible de la base."""
    if not DB_PATH.exists():
        return {
            "error": "Base edupaie.db introuvable. "
                     "Exécuter : pip install -r requirements.txt && python seed_database.py",
        }

    con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()

        eleves = cur.execute(
            """
            SELECT e.id, e.nom, e.prenom, e.montant_total_du,
                   c.nom AS classe, a.libelle AS annee,
                   COALESCE(SUM(p.montant), 0) AS paye
            FROM eleve e
            JOIN classe c ON c.id = e.classe_id
            JOIN annee_scolaire a ON a.id = e.annee_id
            LEFT JOIN paiement p ON p.eleve_id = e.id
            GROUP BY e.id
            ORDER BY c.nom, e.nom, e.prenom
            """
        ).fetchall()

        paiements = cur.execute(
            """
            SELECT p.numero_recu, p.date_paiement, p.mode, p.montant,
                   p.solde_apres, e.nom, e.prenom
            FROM paiement p
            JOIN eleve e ON e.id = p.eleve_id
            ORDER BY p.id DESC
            LIMIT 20
            """
        ).fetchall()

        n_classes = cur.execute("SELECT COUNT(*) FROM classe").fetchone()[0]
        n_annees = cur.execute("SELECT COUNT(*) FROM annee_scolaire").fetchone()[0]
        n_paiements = cur.execute("SELECT COUNT(*) FROM paiement").fetchone()[0]

        liste_eleves = []
        total_du = total_paye = 0
        soldes = partielles = non_payes = 0
        for row in eleves:
            du = int(row["montant_total_du"])
            paye = int(row["paye"])
            restant = du - paye
            total_du += du
            total_paye += paye
            if restant <= 0:
                statut = "Soldé"
                soldes += 1
            elif paye > 0:
                statut = "Partiellement payé"
                partielles += 1
            else:
                statut = "Non payé"
                non_payes += 1
            liste_eleves.append({
                "nom": row["nom"],
                "prenom": row["prenom"],
                "classe": row["classe"],
                "annee": row["annee"],
                "montant_total_du": du,
                "paye": paye,
                "restant": max(restant, 0),
                "statut": statut,
            })

        liste_paiements = [{
            "numero_recu": r["numero_recu"],
            "date_paiement": r["date_paiement"],
            "mode": MODES_PAIEMENT.get(r["mode"], r["mode"]),
            "montant": int(r["montant"]),
            "solde_apres": int(r["solde_apres"]),
            "eleve": f"{r['nom']} {r['prenom']}",
        } for r in paiements]

        return {
            "stats": {
                "eleves": len(eleves),
                "paiements": n_paiements,
                "classes": n_classes,
                "annees": n_annees,
                "total_du": total_du,
                "total_paye": total_paye,
                "total_restant": max(total_du - total_paye, 0),
                "soldes": soldes,
                "partielles": partielles,
                "non_payes": non_payes,
            },
            "eleves": liste_eleves,
            "paiements": liste_paiements,
        }
    finally:
        con.close()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            body = INDEX_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/data":
            payload = json.dumps(fetch_snapshot(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"EduPaie aperçu web : http://127.0.0.1:{port}/ (base : {DB_PATH})")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
