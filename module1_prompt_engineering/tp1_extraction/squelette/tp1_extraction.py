"""TP 1 – Extraire un message client en JSON et comparer trois modèles (SQUELETTE).

Cherchez les « TODO » : il y en a cinq, le dernier est un bonus.

Pour chaque modèle et chaque message du jeu de test :
  1. appeler le modèle avec le prompt d'extraction ;
  2. récupérer le JSON et le valider avec le schéma Pydantic ;
  3. comparer au résultat attendu, mesurer la latence et le coût.

Exemples :
  python tp1_extraction/squelette/tp1_extraction.py --limite 3          # commencez petit !
  python tp1_extraction/squelette/tp1_extraction.py
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import litellm
from dotenv import load_dotenv
from pydantic import ValidationError

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]
sys.path.insert(0, str(ICI.parent))          # evaluation.py
from evaluation import noter, synthese, tableau_markdown  # noqa: E402
from schema import MessageClient  # noqa: E402

load_dotenv(RACINE / ".env")
litellm.drop_params = True                    # ignore les paramètres non pris en charge (ex. temperature)

MESSAGES = RACINE / "data" / "messages_clients.jsonl"
PROMPT = (ICI / "prompt_extraction_v1.txt").read_text(encoding="utf-8")
SORTIE = RACINE / "resultats"


def charger_messages(limite=None):
    with open(MESSAGES, encoding="utf-8") as f:
        messages = [json.loads(l) for l in f if l.strip()]
    return messages[:limite] if limite else messages


def entree_utilisateur(m):
    """Le message est fourni comme une donnée délimitée, avec sa date pour les dates relatives."""
    return f"Date du message : {m['date_message']}\nMessage du client :\n\"\"\"\n{m['message']}\n\"\"\""


def extraire_json(texte: str) -> str:
    """Retire les balises Markdown et le texte autour du JSON."""
    # TODO 2 – Certains modèles répondent « Voici le JSON : ```json {...} ``` ».
    #          Renvoyez uniquement la partie qui va de la première « { » à la dernière « } ».
    return texte


def appeler(modele, m, mode="prompt"):
    params = dict(
        model=modele,
        messages=[{"role": "system", "content": PROMPT},
                  {"role": "user", "content": entree_utilisateur(m)}],
        temperature=0,
    )
    # TODO 3 – Appelez le modèle avec litellm.completion(**params) et mesurez :
    #   - la latence en secondes, avec time.perf_counter() avant et après l'appel ;
    #   - le coût en dollars, avec litellm.completion_cost(completion_response=rep)
    #     (entourez-le d'un try/except : un modèle local n'a pas de prix → cout = None).
    # Renvoyez : le texte de la réponse, la latence, le coût, rep.usage
    rep = litellm.completion(**params)
    latence, cout = 0.0, None
    return rep.choices[0].message.content or "", latence, cout, rep.usage


def analyser(texte):
    """Renvoie (json_valide, schema_valide, données extraites, erreur éventuelle)."""
    # TODO 4 – Décodez le JSON avec json.loads(extraire_json(texte)).
    #          En cas de json.JSONDecodeError : renvoyez (False, False, None, "JSON invalide : ...").
    donnees = None
    # TODO 5 (BONUS) – Validez avec MessageClient.model_validate(donnees) (complétez d'abord schema.py).
    #          Succès : (True, True, objet.model_dump(), None)
    #          ValidationError : (True, False, donnees, "Schéma : ...")
    return donnees is not None, False, donnees, None


def evaluer(modeles, limite=None, mode="prompt"):
    messages = charger_messages(limite)
    lignes = []
    for modele in modeles:
        print(f"\n=== {modele} ({len(messages)} messages, mode {mode})")
        for m in messages:
            try:
                texte, latence, cout, usage = appeler(modele, m, mode)
            except Exception as e:                 # quota, clé absente, modèle inconnu…
                print(f"  {m['id']} ERREUR D'APPEL : {e}")
                texte, latence, cout, usage = "", 0.0, None, None
            json_ok, schema_ok, extrait, erreur = analyser(texte)
            notes = noter(extrait, m["attendu"])
            lignes.append({
                "modele": modele, "id": m["id"], "categorie_attendue": m["attendu"]["categorie"],
                "categorie_obtenue": (extrait or {}).get("categorie"),
                "json_valide": json_ok, "schema_valide": schema_ok, "notes": notes,
                "latence_s": latence, "cout_usd": cout,
                "tokens_entree": getattr(usage, "prompt_tokens", None),
                "tokens_sortie": getattr(usage, "completion_tokens", None),
                "erreur": erreur, "sortie_brute": texte,
            })
            ok = sum(notes.values())
            print(f"  {m['id']} {m['attendu']['categorie']}→{(extrait or {}).get('categorie')} "
                  f"{ok}/{len(notes)} champs  {latence:.2f}s" + (f"  [{erreur}]" if erreur else ""))
    return lignes


def enregistrer(lignes, mode):
    SORTIE.mkdir(exist_ok=True)
    chemin = SORTIE / f"tp1_details_{mode}.csv"
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        champs = list(lignes[0]["notes"])
        w.writerow(["modele", "id", "categorie_attendue", "categorie_obtenue", "json_valide", "schema_valide",
                    *[f"juste_{c}" for c in champs], "latence_s", "cout_usd", "tokens_entree",
                    "tokens_sortie", "erreur", "sortie_brute"])
        for l in lignes:
            w.writerow([l["modele"], l["id"], l["categorie_attendue"], l["categorie_obtenue"], l["json_valide"],
                        l["schema_valide"], *[l["notes"][c] for c in champs], f"{l['latence_s']:.3f}",
                        l["cout_usd"], l["tokens_entree"], l["tokens_sortie"], l["erreur"], l["sortie_brute"]])
    return chemin


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--modeles", nargs="+",
                   default=[x.strip() for x in os.getenv("MODELES_TP1", "").split(",") if x.strip()])
    p.add_argument("--limite", type=int, help="ne traiter que les N premiers messages")
    p.add_argument("--mode", choices=["prompt", "structure"], default="prompt")
    args = p.parse_args()
    if not args.modeles:
        sys.exit("Aucun modèle : renseignez MODELES_TP1 dans .env ou passez --modeles.")

    lignes = evaluer(args.modeles, args.limite, args.mode)
    chemin = enregistrer(lignes, args.mode)
    print("\n" + tableau_markdown(synthese(lignes)))
    erreurs = [l for l in lignes if not l["notes"]["categorie"]]
    if erreurs:
        print("\nErreurs de catégorie (à discuter en groupe) :")
        for l in erreurs:
            print(f"  {l['modele']:35s} {l['id']}  attendu {l['categorie_attendue']}, obtenu {l['categorie_obtenue']}")
    print(f"\nDétail par message : {chemin}")
