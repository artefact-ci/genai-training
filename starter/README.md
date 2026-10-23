# Formation Agents IA & AI Engineering

Fil rouge : un assistant support client pour **Lagune Banque** (données fictives).

## Prérequis

- [uv](https://docs.astral.sh/uv/getting-started/installation/) installé (il se charge aussi d'installer Python 3.11).
- Git.
- Une clé d'API LLM.

## Installation

```bash
git clone --filter=blob:none --sparse <url>
cd formation-agents-ia
git sparse-checkout set starter
cd starter
cp .env.example .env   # puis renseigner la clé
uv sync
uv run scripts/check_env.py
uv run jupyter lab
```

Dans `.env`, renseignez `LLM_API_KEY` et `MODELE` (`MODELE_2` est utilisé dans certains TP).
Le script `check_env.py` doit afficher `OK`. Sinon, le message indique ce qu'il faut corriger.
