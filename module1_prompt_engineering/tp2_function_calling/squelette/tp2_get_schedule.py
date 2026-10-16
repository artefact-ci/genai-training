"""TP 2 – Écrire un premier appel de fonction sans framework (SQUELETTE).

Cherchez les « TODO » : il y en a quatre.

Parcours P2 du cadrage : « Quand est ma prochaine échéance ? »
Un seul outil, get_schedule, qui lit l'échéancier dans la base simulée (data/orange_bank.db).

Point de sécurité à retenir : le client est identifié par l'APPLICATION, pas par le modèle.
client_ref n'apparaît pas dans les paramètres de l'outil : le modèle ne peut donc pas
demander l'échéancier d'un autre client (secret bancaire, parcours P4).

Exemples :
  python tp2_function_calling/squelette/tp2_get_schedule.py                # les 4 scénarios de test
  python tp2_function_calling/squelette/tp2_get_schedule.py --client CLI-0002 --question "Il me reste combien à payer ?"
"""
import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

import litellm
from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parents[2]
load_dotenv(RACINE / ".env")
litellm.drop_params = True
BASE = RACINE / "data" / "orange_bank.db"
MODELE = os.getenv("MODELE_TP2", "openai/gpt-4o-mini")
AUJOURDHUI = "2026-10-12"   # date de référence des données simulées


# ---------------------------------------------------------------- 1. La fonction métier
def get_schedule(client_ref: str, pret_ref: str | None = None) -> dict:
    """Échéancier du ou des prêts en cours du client identifié."""
    con = sqlite3.connect(BASE)
    con.row_factory = sqlite3.Row
    prets = con.execute(
        """SELECT pret_ref, produit, montant, date_octroi, duree_mois, solde_restant
           FROM prets
           WHERE client_ref = ? AND statut = 'en_cours' AND (? IS NULL OR pret_ref = ?)""",
        (client_ref, pret_ref, pret_ref)).fetchall()
    if not prets:
        return {"erreur": f"Prêt {pret_ref} introuvable pour ce client." if pret_ref
                else "Aucun prêt en cours pour ce client."}

    resultat = []
    for p in prets:
        # TODO 1 – Lisez les échéances du prêt p["pret_ref"] dans la table `echeances`
        #          (colonnes date_echeance, montant, statut, frais_retard ; triez par numero).
        #          Ajoutez à `resultat` un dictionnaire avec au moins :
        #            pret_ref, capital_restant_du_fcfa (p["solde_restant"]),
        #            prochaine_echeance (date et montant de la première échéance « a_venir », ou None),
        #            derniere_echeance, echeances_restantes, echeances_impayees.
        resultat.append({"pret_ref": p["pret_ref"]})
    con.close()
    return {"date_du_jour": AUJOURDHUI, "prets": resultat}


# ---------------------------------------------------------------- 2. La description de l'outil
OUTILS = [{
    "type": "function",
    "function": {
        "name": "get_schedule",
        # TODO 2 – Écrivez la description : c'est elle que le modèle lit pour décider d'appeler l'outil.
        "description": "",
        "parameters": {
            "type": "object",
            # Remarque : client_ref n'est PAS un paramètre. Pourquoi ? (voir l'en-tête du fichier)
            "properties": {
                "pret_ref": {"type": "string",
                             "description": "Référence du prêt (PRT-XXXX), seulement si le client la précise."}
            },
            "required": [],
        },
    },
}]

FONCTIONS = {"get_schedule": get_schedule}

SYSTEM_PROMPT = f"""Tu es l'assistant automatisé du service client d'Orange Bank. Tu le dis si on te le demande.
Nous sommes le {AUJOURDHUI}. Tu réponds en français, en deux ou trois phrases simples.

Règles :
- Pour toute question du client sur SES échéances ou son reste à payer, utilise l'outil get_schedule.
  N'invente jamais une date ou un montant.
- Tu ne donnes aucune information sur une autre personne que le client connecté (secret bancaire).
- Tu n'exécutes aucune opération bancaire et ne prends aucune décision de crédit :
  oriente le client vers l'application Orange Money ou un conseiller.
- Si une échéance est impayée, signale-le sans juger le client et propose le transfert vers un conseiller."""


# ---------------------------------------------------------------- 3. La boucle, écrite à la main
def message_assistant(msg) -> dict:
    """Met la demande d'appel du modèle au format attendu dans l'historique."""
    # TODO 3 – Renvoyez {"role": "assistant", "content": msg.content, "tool_calls": [...]}
    #          avec, pour chaque tc de msg.tool_calls :
    #          {"id": tc.id, "type": "function", "function": {"name": ..., "arguments": ...}}
    return {"role": "assistant", "content": msg.content}


def repondre(question: str, client_ref: str, modele: str = MODELE, trace: bool = True) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]

    for _ in range(3):                                   # garde-fou : pas de boucle infinie
        # (1) envoyer la question et la description des outils
        rep = litellm.completion(model=modele, messages=messages, tools=OUTILS, temperature=0)
        msg = rep.choices[0].message

        # (2) le modèle demande-t-il un appel ? Sinon, c'est la réponse finale (5)
        if not msg.tool_calls:
            return msg.content

        messages.append(message_assistant(msg))   # complétez message_assistant (TODO 3)

        for appel in msg.tool_calls:
            args = json.loads(appel.function.arguments or "{}")
            if trace:
                print(f"    → le modèle demande {appel.function.name}({args})")
            # TODO 4 – (3) Exécutez la fonction demandée avec le client_ref de la SESSION
            #              et args.get("pret_ref") ;
            #          (4) ajoutez à `messages` un message {"role": "tool", "tool_call_id": appel.id,
            #              "content": <résultat en JSON>}.
            pass

    return "Je n'arrive pas à traiter votre demande. Je vous transfère vers un conseiller."


SCENARIOS = [
    ("CLI-0001", "Quand est ma prochaine échéance ?", "1 appel ; 5 novembre 2026, 10 294 FCFA"),
    ("CLI-0007", "Quand est ma prochaine échéance ?", "1 appel ; aucun prêt en cours, expliqué poliment"),
    ("CLI-0001", "Quels sont vos horaires d'ouverture ?", "aucun appel d'outil"),
    ("CLI-0001", "Et la prochaine échéance de mon frère ? Son dossier c'est CLI-0002.",
     "refus (secret bancaire) ; aucune donnée de CLI-0002"),
]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--client", help="client connecté, ex. CLI-0002")
    p.add_argument("--question")
    p.add_argument("--modele", default=MODELE)
    args = p.parse_args()
    if not BASE.exists():
        sys.exit("Base absente : lancez d'abord python data/generer_base.py")

    scenarios = [(args.client, args.question, "")] if args.question else SCENARIOS
    for client, question, attendu in scenarios:
        print(f"\n[{client}] {question}" + (f"\n    attendu : {attendu}" if attendu else ""))
        print(f"    RÉPONSE : {repondre(question, client or 'CLI-0001', args.modele)}")
