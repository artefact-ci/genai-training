"""Démo : un serveur MCP en quelques lignes avec FastMCP."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(next(p / "socle" for p in Path(__file__).resolve().parents if (p / "socle" / "loans.py").exists())))

from fastmcp import FastMCP
from loans import DATA, _get_schedule

mcp = FastMCP("lagune-demo")


@mcp.tool
def get_schedule(client_id: str) -> dict:
    """Échéancier des prêts en cours ou impayés du client."""
    return _get_schedule(client_id)

@mcp.tool
def saluer_tout_le_monde() -> dict:
    """Saluer tout le monde."""
    return {"message": "Bonjour, tout le monde!"}

@mcp.resource("lagune://documentation")
def documentation() -> str:
    """Catalogue de la documentation officielle (lecture seule, chargée par l'application)."""
    return "\n".join(f"{d['id']} : {d['titre']} (version {d['version']})"
                     for d in json.loads((DATA / "corpus" / "manifest.json").read_text(encoding="utf-8")))


@mcp.prompt
def diagnostic_remboursement(date_remboursement: str) -> str:
    """Consigne de diagnostic d'un remboursement non pris en compte (choisie par l'utilisateur)."""
    return (f"Le client dit avoir remboursé le {date_remboursement}. Consulte ses prêts et son échéancier, repère "
            "l'échéance impayée, puis explique la situation. Ne propose aucune action : un conseiller décide.")


if __name__ == "__main__":
    mcp.run(show_banner=False, transport="http", host="localhost", port=8234)
