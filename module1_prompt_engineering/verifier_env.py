"""Vérifie l'environnement avant les TP du module 1.

  python verifier_env.py           # vérifications locales
  python verifier_env.py --ping    # + un appel réel à chaque modèle configuré (consomme quelques tokens)
"""
import importlib
import os
import sqlite3
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
ok = True


def etat(bon, texte, conseil=""):
    global ok
    ok &= bon
    print(("  [OK]   " if bon else "  [ÉCHEC] ") + texte + ("" if bon or not conseil else f"\n           → {conseil}"))


print("Python et bibliothèques")
etat(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (3.10 minimum)")
for mod in ["litellm", "pydantic", "dotenv"]:
    try:
        importlib.import_module(mod)
        etat(True, mod)
    except ImportError:
        etat(False, mod, "pip install -r requirements.txt")

print("Données")
base = RACINE / "data" / "orange_bank.db"
if base.exists():
    n = sqlite3.connect(base).execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    etat(n >= 30, f"base simulée : {n} clients")
else:
    etat(False, "base simulée absente", "python data/generer_base.py")
msgs = RACINE / "data" / "messages_clients.jsonl"
etat(msgs.exists() and sum(1 for _ in open(msgs, encoding="utf-8")) == 30, "jeu de 30 messages clients",
     "python data/construire_messages.py")

print("Modèles")
try:
    from dotenv import load_dotenv
    load_dotenv(RACINE / ".env")
except ImportError:
    pass
modeles = [m.strip() for m in os.getenv("MODELES_TP1", "").split(",") if m.strip()]
etat(len(modeles) == 3, f"MODELES_TP1 : {modeles or 'non renseigné'}", "copiez .env.example en .env et complétez")
etat(bool(os.getenv("MODELE_TP2")), f"MODELE_TP2 : {os.getenv('MODELE_TP2') or 'non renseigné'}")

if "--ping" in sys.argv and modeles:
    import litellm
    litellm.drop_params = True
    for m in dict.fromkeys(modeles + [os.getenv("MODELE_TP2", "")]):
        if not m:
            continue
        try:
            litellm.completion(model=m, messages=[{"role": "user", "content": "Réponds OK"}], max_tokens=5)
            etat(True, f"appel {m}")
        except Exception as e:
            etat(False, f"appel {m} : {str(e)[:120]}", "vérifiez la clé API et le nom du modèle")

print("\nTout est prêt." if ok else "\nCorrigez les points en échec avant le TP.")
sys.exit(0 if ok else 1)
