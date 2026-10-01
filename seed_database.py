"""
Script de peuplement de la base de données avec des données de test.

Crée des classes, années, élèves et paiements avec des noms togolais/ouest-africains.
"""

from data.database import initialize_database
from services.classe_service import ClasseService
from services.annee_service import AnneeService
from services.eleve_service import EleveService
from services.paiement_service import PaiementService
from datetime import datetime

def seed_database():
    """Peuple la base de données avec des données de test."""
    print("=== Peuplement de la base de données ===\n")
    
    # Créer les classes
    print("--- Création des classes ---")
    classes = [
        "CP1", "CP2", "CE1", "CE2", "CM1", "CM2", "6ème", "5ème", "4ème", "3ème"
    ]
    classe_ids = {}
    for nom in classes:
        try:
            cid = ClasseService.creer_classe(nom)
            classe_ids[nom] = cid
            print(f"[OK] Classe créée : {nom} (ID: {cid})")
        except Exception as e:
            # La classe existe peut-être déjà
            existing = ClasseService.get_all_classes()
            for c in existing:
                if c['nom'] == nom:
                    classe_ids[nom] = c['id']
                    print(f"[INFO] Classe existante : {nom} (ID: {c['id']})")
                    break
    
    # Créer les années scolaires
    print("\n--- Création des années scolaires ---")
    annees = ["2023-2024", "2024-2025"]
    annee_ids = {}
    for libelle in annees:
        try:
            aid = AnneeService.creer_annee(libelle)
            annee_ids[libelle] = aid
            print(f"[OK] Année créée : {libelle} (ID: {aid})")
        except Exception as e:
            existing = AnneeService.get_all_annees()
            for a in existing:
                if a['libelle'] == libelle:
                    annee_ids[libelle] = a['id']
                    print(f"[INFO] Année existante : {libelle} (ID: {a['id']})")
                    break
    
    # Créer les élèves avec des noms togolais/ouest-africains
    print("\n--- Création des élèves ---")
    eleves_data = [
        # Élèves soldés
        ("Koffi", "Yawovi", "CM2", "2024-2025", 250000, True),
        ("Aho", "Komi", "CM2", "2024-2025", 300000, True),
        ("Mensah", "Kofi", "CM1", "2024-2025", 200000, True),
        
        # Élèves partiellement payés
        ("Agbé", "Koffi", "CM2", "2024-2025", 280000, False),
        ("Kouassi", "Adjoa", "CE2", "2024-2025", 180000, False),
        ("Koffi", "Mawuli", "CM1", "2024-2025", 220000, False),
        ("Ametepe", "Kofi", "CM2", "2024-2025", 260000, False),
        ("Kokou", "Sena", "CE1", "2024-2025", 150000, False),
        
        # Élèves non payés
        ("Téko", "Komlan", "CM2", "2024-2025", 290000, False),
        ("Gnassingbé", "Faustin", "CM1", "2024-2025", 210000, False),
        ("Agbodjè", "Djimon", "CE2", "2024-2025", 170000, False),
        ("Kouamé", "Yao", "CM2", "2024-2025", 275000, False),
        ("Tchanilé", "Koffi", "CM1", "2024-2025", 230000, False),
        ("Assio", "Kwami", "CE1", "2024-2025", 160000, False),
        ("Kpakpa", "Komi", "CM2", "2024-2025", 285000, False),
    ]
    
    eleve_ids = []
    for nom, prenom, classe, annee, montant, soldé in eleves_data:
        try:
            eid = EleveService.creer_eleve(
                nom, prenom,
                classe_ids[classe],
                annee_ids[annee],
                montant
            )
            eleve_ids.append((eid, nom, prenom, montant, soldé))
            print(f"[OK] Élève créé : {nom} {prenom} ({classe}) - {montant} FCFA")
        except Exception as e:
            print(f"[ERREUR] Élève {nom} {prenom} : {e}")
    
    # Créer les paiements
    print("\n--- Création des paiements ---")
    modes_paiement = ["especes", "cheque", "virement", "mobile_money"]
    
    from random import choice, randint
    from datetime import timedelta
    
    for eid, nom, prenom, montant, soldé in eleve_ids:
        if soldé:
            # Payer en plusieurs fois pour atteindre le total
            restant = montant
            while restant > 0:
                montant_paiement = min(restant, randint(25000, 100000))
                date = (datetime.now() - timedelta(days=randint(1, 180))).strftime("%d/%m/%Y")
                mode = choice(modes_paiement)
                
                try:
                    pid = PaiementService.enregistrer_paiement(
                        eid, montant_paiement, date, mode
                    )
                    print(f"[OK] Paiement : {nom} {prenom} - {montant_paiement} FCFA ({mode})")
                    restant -= montant_paiement
                except Exception as e:
                    print(f"[ERREUR] Paiement {nom} {prenom} : {e}")
                    break
        else:
            # Payer partiellement (50-80% du total)
            if randint(0, 1) == 1:  # 50% de chance d'avoir des paiements
                total_paye = montant * randint(50, 80) // 100
                restant = total_paye
                while restant > 0:
                    montant_paiement = min(restant, randint(25000, 75000))
                    date = (datetime.now() - timedelta(days=randint(1, 180))).strftime("%d/%m/%Y")
                    mode = choice(modes_paiement)
                    
                    try:
                        pid = PaiementService.enregistrer_paiement(
                            eid, montant_paiement, date, mode
                        )
                        print(f"[OK] Paiement : {nom} {prenom} - {montant_paiement} FCFA ({mode})")
                        restant -= montant_paiement
                    except Exception as e:
                        print(f"[ERREUR] Paiement {nom} {prenom} : {e}")
                        break
    
    print("\n=== Peuplement terminé ===")
    print(f"Élèves créés : {len(eleve_ids)}")
    print(f"Classes : {len(classe_ids)}")
    print(f"Années : {len(annee_ids)}")


if __name__ == "__main__":
    initialize_database()
    seed_database()
