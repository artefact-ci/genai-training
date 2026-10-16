"""Génère data/orange_bank.db : la base SQLite simulée du fil rouge (cadrage, §9.1).

Toutes les données sont FICTIVES et ne reflètent pas les procédures d'Orange Bank.
Date de référence (« aujourd'hui » pendant la formation) : lundi 12 octobre 2026.

Tables : clients, prets, echeances, transactions_om, comptes_epargne, mouvements_epargne,
         incidents_plateforme, reclamations, regularisations

Cas prévus pour le scénario P3 (cadrage, §6.3), un par issue :
  CLI-0002 M. Kouassi  transaction RÉUSSIE mais NON RATTACHÉE (incident plateforme le jour même)
  CLI-0004 M. Traoré   transaction EN ÉCHEC
  CLI-0005 Mme Diallo  transaction INTROUVABLE
Autres cas utiles :
  CLI-0001 Aminata     prêt étudiant à jour (parcours P2, TP 2)
  CLI-0003 Mme Bamba   épargnante, sans prêt (P1)
  CLI-0006 M. N'Guessan prêt souscrit la veille au soir, signalé comme frauduleux (P5)
  CLI-0007 Mme Ouattara aucun prêt en cours (TP 2 : cas « pas de prêt »)
  CLI-0008 M. Koffi    transaction réussie non rattachée, sans incident plateforme

Usage : python data/generer_base.py   (recrée la base à chaque exécution, résultat identique)
"""
import json
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

AUJOURDHUI = date(2026, 10, 12)
FRAIS_RETARD = 2500          # FCFA, forfaitaire (fictif : à aligner sur la grille des frais du corpus)
DELAI_RATTACHEMENT_H = 2     # heures (cadrage, §6.4)
TAUX = {"pret_etudiant": 0.10, "pret_personnel": 0.12, "pret_commercant": 0.14}

BASE = Path(__file__).parent / "orange_bank.db"
rng = random.Random(42)

SCHEMA = """
CREATE TABLE clients (
    client_ref TEXT PRIMARY KEY, prenom TEXT, nom TEXT, numero_om TEXT,
    statut_kyc TEXT CHECK (statut_kyc IN ('valide', 'en_attente')),
    acces_nouveau_pret TEXT CHECK (acces_nouveau_pret IN ('actif', 'suspendu')),
    persona TEXT
);
CREATE TABLE prets (
    pret_ref TEXT PRIMARY KEY, client_ref TEXT REFERENCES clients,
    produit TEXT, montant INTEGER, date_octroi TEXT, duree_mois INTEGER, taux_annuel REAL,
    statut TEXT CHECK (statut IN ('en_cours', 'solde')), solde_restant INTEGER
);
CREATE TABLE echeances (
    echeance_id INTEGER PRIMARY KEY, pret_ref TEXT REFERENCES prets, numero INTEGER,
    date_echeance TEXT, montant INTEGER, part_capital INTEGER, part_interets INTEGER,
    statut TEXT CHECK (statut IN ('payee', 'a_venir', 'impayee')), frais_retard INTEGER DEFAULT 0
);
CREATE TABLE transactions_om (
    transaction_ref TEXT PRIMARY KEY, client_ref TEXT REFERENCES clients, date_heure TEXT,
    montant INTEGER, type TEXT, statut TEXT CHECK (statut IN ('reussie', 'echec')),
    motif_echec TEXT, pret_ref TEXT, echeance_id INTEGER  -- NULL = non rattachée à une échéance
);
CREATE TABLE comptes_epargne (
    compte_ref TEXT PRIMARY KEY, client_ref TEXT REFERENCES clients,
    solde INTEGER, taux_annuel REAL, date_ouverture TEXT
);
CREATE TABLE mouvements_epargne (
    mouvement_id INTEGER PRIMARY KEY, compte_ref TEXT REFERENCES comptes_epargne,
    date TEXT, type TEXT CHECK (type IN ('depot', 'retrait', 'interets')), montant INTEGER
);
CREATE TABLE incidents_plateforme (
    incident_id TEXT PRIMARY KEY, debut TEXT, fin TEXT, services TEXT, description TEXT
);
CREATE TABLE reclamations (
    reclamation_id TEXT PRIMARY KEY, client_ref TEXT REFERENCES clients, date_creation TEXT,
    motif TEXT, statut TEXT CHECK (statut IN ('ouverte', 'en_cours', 'cloturee')), dossier_json TEXT
);
CREATE TABLE regularisations (
    regularisation_id TEXT PRIMARY KEY, client_ref TEXT REFERENCES clients, pret_ref TEXT,
    echeance_id INTEGER, transaction_ref TEXT, action TEXT, montant INTEGER,
    statut TEXT CHECK (statut IN ('proposee', 'validee', 'refusee')),
    validateur TEXT, date_demande TEXT, date_validation TEXT
);
"""


def ajoute_mois(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    return date(a, m, min(d.day, 28))


def echeancier(montant, taux_annuel, mois):
    """Mensualités constantes ; la dernière absorbe l'arrondi."""
    t = taux_annuel / 12
    mensualite = round(montant * t / (1 - (1 + t) ** -mois))
    lignes, restant = [], montant
    for k in range(1, mois + 1):
        interets = round(restant * t)
        capital = restant if k == mois else mensualite - interets
        restant -= capital
        lignes.append((k, capital + interets, capital, interets))
    return lignes


class Generateur:
    def __init__(self, con):
        self.con = con
        self.n_pret = 100
        self.n_tx = 0

    def client(self, ref, prenom, nom, persona="", kyc="valide", acces="actif"):
        num = f"07 00 {int(ref[-2:]):02d} {rng.randint(10, 99)} {rng.randint(10, 99)}"
        self.con.execute("INSERT INTO clients VALUES (?,?,?,?,?,?,?)",
                         (ref, prenom, nom, num, kyc, acces, persona))

    def tx(self, client_ref, quand: datetime, montant, statut="reussie", motif_echec=None,
           pret_ref=None, echeance_id=None):
        self.n_tx += 1
        ref = f"OM{quand:%y%m%d}.{self.n_tx:04d}"
        self.con.execute("INSERT INTO transactions_om VALUES (?,?,?,?,?,?,?,?,?)",
                         (ref, client_ref, quand.isoformat(timespec="minutes"), montant,
                          "remboursement_pret", statut, motif_echec, pret_ref, echeance_id))
        return ref

    def pret(self, client_ref, produit, montant, octroi: date, mois, cas=None):
        """Crée un prêt et son échéancier. Les échéances passées sont payées et rattachées,
        sauf la dernière échue si `cas` est 'non_rattachee', 'echec' ou 'introuvable'."""
        self.n_pret += 1
        ref = f"PRT-{self.n_pret:04d}"
        taux = TAUX[produit]
        lignes = echeancier(montant, taux, mois)
        echues = [l for l in lignes if ajoute_mois(octroi, l[0]) <= AUJOURDHUI]
        capital_paye = 0
        ids = {}
        for k, mt, cap, inte in lignes:
            d = ajoute_mois(octroi, k)
            statut = "payee" if d <= AUJOURDHUI else "a_venir"
            frais = 0
            if cas and echues and k == echues[-1][0]:
                statut, frais = "impayee", FRAIS_RETARD
            cur = self.con.execute(
                "INSERT INTO echeances (pret_ref, numero, date_echeance, montant, part_capital, "
                "part_interets, statut, frais_retard) VALUES (?,?,?,?,?,?,?,?)",
                (ref, k, d.isoformat(), mt, cap, inte, statut, frais))
            ids[k] = (cur.lastrowid, d, mt)
            if statut == "payee":
                capital_paye += cap
                h = datetime(d.year, d.month, d.day, rng.randint(7, 20), rng.randint(0, 59))
                self.tx(client_ref, h - timedelta(days=rng.randint(0, 2)), mt, pret_ref=ref,
                        echeance_id=cur.lastrowid)
        statut_pret = "solde" if capital_paye == montant else "en_cours"
        self.con.execute("INSERT INTO prets VALUES (?,?,?,?,?,?,?,?,?)",
                         (ref, client_ref, produit, montant, octroi.isoformat(), mois, taux,
                          statut_pret, montant - capital_paye))
        return ref, ids, echues


def generer():
    if BASE.exists():
        BASE.unlink()
    con = sqlite3.connect(BASE)
    con.executescript(SCHEMA)
    g = Generateur(con)

    # --- Aminata : prêt étudiant à jour (P1, P2)
    g.client("CLI-0001", "Aminata", "Koné", "Aminata – étudiante, petit prêt")
    g.pret("CLI-0001", "pret_etudiant", 60000, date(2026, 8, 5), 6)

    # --- M. Kouassi : prêts récurrents, remboursement d'hier non rattaché (P3, issue 1)
    g.client("CLI-0002", "Yao", "Kouassi", "M. Kouassi – commerçant, prêts récurrents", acces="suspendu")
    ancien, ids_anc, _ = g.pret("CLI-0002", "pret_commercant", 200000, date(2025, 11, 11), 6)
    ref, ids, echues = g.pret("CLI-0002", "pret_commercant", 300000, date(2026, 7, 11), 6, cas="non_rattachee")
    eid, d_ech, mt = ids[echues[-1][0]]   # échéance du 2026-10-11
    tx_kouassi = g.tx("CLI-0002", datetime(2026, 10, 11, 9, 14), mt, pret_ref=ref, echeance_id=None)
    con.execute("INSERT INTO incidents_plateforme VALUES (?,?,?,?,?)",
                ("INC-2026-031", "2026-10-11T08:30", "2026-10-11T11:45", "rattachement_remboursements",
                 "Retard de rattachement des remboursements Orange Money aux échéances de prêt."))
    # Précédent : une première régularisation en avril (« c'est la deuxième fois »)
    eid_avr = ids_anc[5][0]
    tx_avr = con.execute("SELECT transaction_ref FROM transactions_om WHERE echeance_id = ?",
                         (eid_avr,)).fetchone()[0]   # paiement d'avril, rattaché après régularisation
    con.execute("INSERT INTO regularisations VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("REG-2026-004", "CLI-0002", ancien, eid_avr, tx_avr,
                 "Rattachement de la transaction, annulation des frais de retard, levée de la suspension",
                 FRAIS_RETARD, "validee", "Conseiller C. Aka", "2026-04-12T10:20", "2026-04-12T14:05"))
    dossier = {"client_ref": "CLI-0002", "parcours": "P3", "motif": "Remboursement non rattaché",
               "elements_collectes": {"dates": ["2026-04-11"], "transaction": tx_avr},
               "verifications": ["transaction réussie", "non rattachée"],
               "action_proposee": "Régularisation", "sources": ["Procédure de régularisation N-1"],
               "urgence": "haute", "sentiment": "mecontent"}
    con.execute("INSERT INTO reclamations VALUES (?,?,?,?,?,?)",
                ("REC-2026-0112", "CLI-0002", "2026-04-12T09:47", "Remboursement non pris en compte",
                 "cloturee", json.dumps(dossier, ensure_ascii=False)))

    # --- Mme Bamba : épargnante, pas de prêt (P1)
    g.client("CLI-0003", "Mariam", "Bamba", "Mme Bamba – épargnante")

    # --- M. Traoré : transaction en échec (P3, issue 2)
    g.client("CLI-0004", "Ibrahim", "Traoré", "Cas P3 – transaction en échec")
    ref, ids, echues = g.pret("CLI-0004", "pret_personnel", 100000, date(2026, 6, 8), 6, cas="echec")
    eid, d_ech, mt = ids[echues[-1][0]]
    g.tx("CLI-0004", datetime(2026, 10, 8, 18, 41), mt, statut="echec",
         motif_echec="solde_insuffisant", pret_ref=ref)

    # --- Mme Diallo : transaction introuvable (P3, issue 3)
    g.client("CLI-0005", "Fatou", "Diallo", "Cas P3 – transaction introuvable")
    g.pret("CLI-0005", "pret_personnel", 150000, date(2026, 5, 9), 6, cas="introuvable")

    # --- M. N'Guessan : prêt souscrit la veille au soir, contesté (P5)
    g.client("CLI-0006", "Paul", "N'Guessan", "Client signalant une fraude")
    g.pret("CLI-0006", "pret_personnel", 150000, date(2026, 10, 11), 3)

    # --- Mme Ouattara : aucun prêt en cours (TP 2)
    g.client("CLI-0007", "Awa", "Ouattara", "Aucun prêt en cours")
    g.pret("CLI-0007", "pret_etudiant", 40000, date(2025, 12, 3), 3)   # soldé

    # --- M. Koffi : réussie non rattachée, sans incident
    g.client("CLI-0008", "Serge", "Koffi", "Cas P3 – non rattachée sans incident")
    ref, ids, echues = g.pret("CLI-0008", "pret_commercant", 250000, date(2026, 4, 2), 12, cas="non_rattachee")
    eid, d_ech, mt = ids[echues[-1][0]]
    g.tx("CLI-0008", datetime(2026, 10, 2, 7, 55), mt, pret_ref=ref, echeance_id=None)

    # --- Clients génériques
    prenoms = ["Adjoua", "Konan", "Aya", "Kouadio", "Affoué", "Moussa", "Salimata", "Brou", "Akissi",
               "Drissa", "Mariétou", "Hervé", "Rokia", "Jean-Marc", "Ange", "Fanta", "Didier", "Nadège",
               "Seydou", "Christelle", "Lassina", "Edwige"]
    noms = ["Yao", "Konaté", "Kouamé", "Coulibaly", "Brou", "Touré", "Gbagbo", "Assi", "Doumbia",
            "Kra", "Sangaré", "Ehui", "Fofana", "Aké", "Ballo", "Tanoh", "Cissé", "Gnahoré", "Dosso",
            "Amani", "Kambou", "Zadi"]
    for i, (p, n) in enumerate(zip(prenoms, noms), start=9):
        ref_c = f"CLI-{i:04d}"
        g.client(ref_c, p, n, kyc="en_attente" if i == 27 else "valide")
        tirage = rng.random()
        if tirage < 0.75:
            produit = rng.choice(list(TAUX))
            montant = {"pret_etudiant": rng.choice([30000, 50000, 75000, 100000]),
                       "pret_personnel": rng.choice([50000, 100000, 150000, 250000]),
                       "pret_commercant": rng.choice([150000, 300000, 400000, 500000])}[produit]
            duree = rng.choice([3, 6, 12])
            octroi = AUJOURDHUI - timedelta(days=rng.randint(20, 330))
            g.pret(ref_c, produit, montant, octroi, duree)

    # --- Épargne
    def epargne(client_ref, ouverture, depots):
        cref = f"EPG-{client_ref[-4:]}"
        solde = 0
        for j, (d, typ, mt) in enumerate(depots):
            solde += mt if typ != "retrait" else -mt
            con.execute("INSERT INTO mouvements_epargne (compte_ref, date, type, montant) VALUES (?,?,?,?)",
                        (cref, d, typ, mt))
        con.execute("INSERT INTO comptes_epargne VALUES (?,?,?,?,?)",
                    (cref, client_ref, solde, 0.035, ouverture))

    epargne("CLI-0003", "2025-03-14", [("2025-03-14", "depot", 500000), ("2025-09-01", "depot", 400000),
                                       ("2025-12-31", "interets", 21450), ("2026-02-15", "depot", 350000),
                                       ("2026-06-30", "interets", 19800), ("2026-08-20", "retrait", 40000)])
    epargne("CLI-0007", "2026-01-10", [("2026-01-10", "depot", 25000), ("2026-06-30", "interets", 420)])
    for i in rng.sample(range(9, 31), 6):
        d0 = AUJOURDHUI - timedelta(days=rng.randint(60, 600))
        epargne(f"CLI-{i:04d}", d0.isoformat(), [(d0.isoformat(), "depot", rng.choice([10000, 25000, 50000, 100000]))])

    con.execute("INSERT INTO incidents_plateforme VALUES (?,?,?,?,?)",
                ("INC-2026-027", "2026-09-03T14:10", "2026-09-03T15:00", "application_mobile",
                 "Indisponibilité partielle de l'application, sans effet sur les remboursements."))
    con.commit()
    return con


if __name__ == "__main__":
    con = generer()
    print(f"Base créée : {BASE}")
    for t in ["clients", "prets", "echeances", "transactions_om", "comptes_epargne", "mouvements_epargne",
              "incidents_plateforme", "reclamations", "regularisations"]:
        print(f"  {t:22s} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:4d} lignes")
