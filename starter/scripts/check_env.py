"""Vérifie que l'environnement est prêt : fichier .env, clé API et appel au modèle."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parent.parent


def echec(message: str) -> None:
    print(f"ÉCHEC : {message}")
    sys.exit(1)


def main() -> None:
    load_dotenv(RACINE / ".env")

    manquantes = [v for v in ("LLM_API_KEY", "MODELE") if not os.getenv(v, "").strip()]
    if manquantes:
        echec(
            f"variable(s) non renseignée(s) : {', '.join(manquantes)}. "
            "Copiez .env.example en .env puis complétez-le."
        )

    import litellm

    try:
        reponse = litellm.completion(
            model=os.environ["MODELE"],
            api_key=os.environ["LLM_API_KEY"],
            messages=[{"role": "user", "content": "Réponds en une phrase : bonjour !"}],
            max_tokens=50,
        )
    except litellm.AuthenticationError:
        echec("clé API refusée. Vérifiez LLM_API_KEY dans le fichier .env.")
    except litellm.NotFoundError:
        echec("modèle introuvable. Vérifiez la valeur de MODELE dans le fichier .env.")
    except litellm.BadRequestError:
        echec("requête invalide. Vérifiez le format de MODELE (ex. fournisseur/nom-du-modèle).")
    except (litellm.APIConnectionError, litellm.Timeout):
        echec("impossible de joindre le fournisseur. Vérifiez votre connexion réseau.")
    except Exception as e:
        echec(f"appel au modèle impossible ({type(e).__name__}).")

    texte = (reponse.choices[0].message.content or "").strip()
    print(f"OK : le modèle {os.environ['MODELE']} répond : {texte}")


if __name__ == "__main__":
    main()
