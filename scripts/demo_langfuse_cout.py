import os
import sys
from pathlib import Path

import litellm
from dotenv import load_dotenv
from langfuse import propagate_attributes

racine = Path(__file__).resolve().parent.parent
load_dotenv(racine / ".env")
sys.path.insert(0, str(racine / "code_partage"))

from observability import clear_langfuse, langfuse_client

litellm.suppress_debug_info = True

if os.getenv("PRIX_ENTREE_1M") and os.getenv("PRIX_SORTIE_1M"):
    litellm.register_model({os.environ["MODELE"]: {
        "input_cost_per_token": float(os.environ["PRIX_ENTREE_1M"]) / 1_000_000,
        "output_cost_per_token": float(os.environ["PRIX_SORTIE_1M"]) / 1_000_000,
        "litellm_provider": os.environ["MODELE"].split("/")[0] if "/" in os.environ["MODELE"] else "openai",
        "mode": "chat",
    }})

QUESTIONS = [
    "Explique en une phrase ce qu'est un token.",
    "Donne trois risques d'un chatbot bancaire sans garde-fous.",
    "Résume en deux lignes la différence entre RAG et fine-tuning.",
    "Écris un court message pour rassurer un client dont la carte est bloquée.",
    "Pourquoi mesurer le coût par appel quand on passe en production ?",
]


def appeler(langfuse, question: str) -> str:
    """Un appel au modèle, enregistré dans Langfuse avec ses tokens et son coût."""
    modele = os.environ["MODELE"]
    messages = [{"role": "user", "content": question}]
    with langfuse.start_as_current_observation(as_type="generation", name="appel-llm", model=modele, input=messages) as gen:
        r = litellm.completion(model=modele, api_key=os.environ["LLM_API_KEY"], messages=messages, max_tokens=200, num_retries=3)
        try:
            cout = litellm.completion_cost(completion_response=r)
        except Exception:                    # modèle absent de la grille de prix LiteLLM : Langfuse calculera lui-même s'il le connaît
            cout = None
        gen.update(
            output=r.choices[0].message.content,
            usage_details={"input": r.usage.prompt_tokens, "output": r.usage.completion_tokens},
            **({"cost_details": {"total": cout}} if cout is not None else {}),
        )
    return r.choices[0].message.content


def main() -> None:
    langfuse = langfuse_client()
    if langfuse is None:
        sys.exit("Langfuse n'est pas configuré : renseignez LANGFUSE_PUBLIC_KEY et LANGFUSE_SECRET_KEY dans .env.")

    with langfuse.start_as_current_observation(as_type="span", name="demo-cout", input=QUESTIONS), \
            propagate_attributes(trace_name="demo-cout", tags=["demo"]):
        for i, question in enumerate(QUESTIONS, 1):
            reponse = appeler(langfuse, question)
            print(f"[{i}/{len(QUESTIONS)}] {question}\n    -> {reponse.strip()[:120]}\n")

    clear_langfuse()
    print("Terminé. Ouvrez Langfuse : Tracing > Traces > demo-cout.")


if __name__ == "__main__":
    main()
