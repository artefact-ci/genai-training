# Module 1 : fondamentaux de la GenAI et prompting

| Notebook | Description |
|---|---|
| `demos/demo2_sampling/` | Observer l'effet de `temperature`, `top_p` et `seed`, puis la limite de `max_tokens` |
| `demos/demo3_hallucination/` | Comparer une réponse sans documentation et une réponse avec source consultable |
| `demos/demo5_structured_output/` | Extraire des données avec un JSON demandé dans le prompt ou imposé par un schéma |
| `tp1_extraction_json/` | Extraire une réclamation avec un schéma Pydantic |
| `demos/demo6_function_calling/` | Suivre un appel d'outil, de la demande du modèle à l'exécution par le code |
| `tp2_function_calling/` | Implémenter la boucle d'appel d'outil sur les données de Lagune Banque |

## Prérequis

- `.env` : `LLM_API_KEY` et `MODELE`.
- La démo 2 charge la documentation de `data/corpus/`. Le TP2 lit `data/banque.db`.
