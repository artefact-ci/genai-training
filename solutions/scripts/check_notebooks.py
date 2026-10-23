"""Exécute les notebooks de solutions/ et de starter/*/demos/ sans les modifier.

À lancer depuis starter/ : uv run python ../solutions/scripts/check_notebooks.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
STARTER = RACINE_DEPOT / "starter"
DELAI_SECONDES = 600


def lister_notebooks() -> list[Path]:
    candidats = list((RACINE_DEPOT / "solutions").rglob("*.ipynb"))
    candidats += STARTER.glob("*/demos/**/*.ipynb")
    return sorted(p for p in candidats if ".ipynb_checkpoints" not in p.parts)


def executer(notebook: Path, sortie: Path) -> tuple[bool, str]:
    """Exécute un notebook depuis starter/ ; la sortie va dans un dossier temporaire."""
    # `python -m nbconvert` équivaut à `jupyter nbconvert` sans passer par le lanceur
    # jupyter.exe, que certaines politiques Windows bloquent.
    commande = [
        "uv", "run", "python", "-m", "nbconvert",
        "--to", "notebook", "--execute",
        "--output-dir", str(sortie),
        f"--ExecutePreprocessor.timeout={DELAI_SECONDES}",
        str(notebook),
    ]
    try:
        r = subprocess.run(
            commande, cwd=STARTER, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        return False, "commande `uv` introuvable"
    if r.returncode == 0:
        return True, ""
    lignes = [ligne for ligne in r.stderr.strip().splitlines() if ligne.strip()]
    return False, lignes[-1] if lignes else f"code de retour {r.returncode}"


def main() -> int:
    notebooks = lister_notebooks()
    if not notebooks:
        print("Aucun notebook trouvé dans solutions/ ni dans starter/*/demos/.")
        return 0

    resultats = []
    with tempfile.TemporaryDirectory() as tmp:
        for nb in notebooks:
            ok, detail = executer(nb, Path(tmp))
            resultats.append((nb.relative_to(RACINE_DEPOT).as_posix(), ok, detail))
            print(f"  {'OK' if ok else 'ÉCHEC':<6} {resultats[-1][0]}", flush=True)

    largeur = max(len(nom) for nom, _, _ in resultats)
    print(f"\n{'Notebook':<{largeur}}  Résultat")
    print(f"{'-' * largeur}  --------")
    for nom, ok, detail in resultats:
        print(f"{nom:<{largeur}}  {'OK' if ok else 'ÉCHEC'}")
        if not ok:
            print(f"{'':<{largeur}}  -> {detail}")

    echecs = sum(1 for _, ok, _ in resultats if not ok)
    print(f"\n{len(resultats) - echecs}/{len(resultats)} notebooks OK")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
