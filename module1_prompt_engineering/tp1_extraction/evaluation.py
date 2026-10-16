"""Évaluation commune au TP 1 (fournie : les participants n'ont pas à la modifier).

Compare une sortie extraite à la sortie attendue du jeu de test, champ par champ.
Le champ « motif » est un résumé libre : il n'est pas noté automatiquement.
"""
from collections import defaultdict

CHAMPS_NOTES = ["categorie", "produit", "dates", "montants_fcfa", "urgence", "sentiment"]


def _normalise(champ, valeur):
    if champ in ("dates", "montants_fcfa"):
        if not isinstance(valeur, list):
            return None
        try:
            return sorted({int(v) for v in valeur}) if champ == "montants_fcfa" else sorted({str(v) for v in valeur})
        except (TypeError, ValueError):
            return None
    return valeur.strip().lower() if isinstance(valeur, str) else valeur


def noter(extrait: dict | None, attendu: dict) -> dict:
    """Renvoie {champ: True/False} pour chaque champ noté. Un extrait absent compte faux partout."""
    if not isinstance(extrait, dict):
        return {c: False for c in CHAMPS_NOTES}
    return {c: _normalise(c, extrait.get(c)) == _normalise(c, attendu.get(c)) for c in CHAMPS_NOTES}


def synthese(lignes: list[dict]) -> list[dict]:
    """Agrège les résultats par modèle : une ligne du tableau livrable par modèle."""
    par_modele = defaultdict(list)
    for l in lignes:
        par_modele[l["modele"]].append(l)
    tableau = []
    for modele, ls in par_modele.items():
        n = len(ls)
        couts = [l["cout_usd"] for l in ls if l["cout_usd"] is not None]
        ligne = {
            "modele": modele,
            "messages": n,
            "json_valide": sum(l["json_valide"] for l in ls),
            "schema_valide": sum(l["schema_valide"] for l in ls),
            "champs_justes": sum(sum(l["notes"].values()) for l in ls),
            "champs_total": n * len(CHAMPS_NOTES),
            "latence_moy_s": sum(l["latence_s"] for l in ls) / n,
            "cout_1000_msg_usd": (sum(couts) / len(couts) * 1000) if couts else None,
        }
        for c in CHAMPS_NOTES:
            ligne[f"juste_{c}"] = sum(l["notes"][c] for l in ls)
        tableau.append(ligne)
    return tableau


def tableau_markdown(tableau: list[dict]) -> str:
    entete = "| Modèle | JSON valide | Schéma valide | Champs justes | Catégorie | Urgence | Latence moy. | Coût / 1 000 msg |"
    sep = "|---|---|---|---|---|---|---|---|"
    lignes = [entete, sep]
    for t in tableau:
        n = t["messages"]
        cout = f"{t['cout_1000_msg_usd']:.3f} $" if t["cout_1000_msg_usd"] is not None else "n/d"
        lignes.append(
            f"| {t['modele']} | {t['json_valide']}/{n} | {t['schema_valide']}/{n} | "
            f"{t['champs_justes']}/{t['champs_total']} ({t['champs_justes'] / t['champs_total']:.0%}) | "
            f"{t['juste_categorie']}/{n} | {t['juste_urgence']}/{n} | {t['latence_moy_s']:.2f} s | {cout} |"
        )
    return "\n".join(lignes)
