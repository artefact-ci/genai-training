# Module 2 : RAG et données métier

| Notebook | Description |
|---|---|
| `demos/demo1_chunking/` | Visualiser le découpage fixe, récursif, par structure et sémantique, ainsi que le cas des tableaux |
| `tp1_chunking/` | Implémenter un splitter, mesurer des distances d'embeddings et comparer six index |
| `demos/demo2_query_rewriting/` | Comparer la réécriture, la multi-requête avec fusion RRF et HyDE |
| `tp2_hybrid_reranking/` | Combiner BM25 et recherche vectorielle avec RRF, puis reclasser les candidats |
| `demos/demo3_grounding_check/` | Comparer la vérification des sources, des chiffres et des affirmations par un modèle juge |
| `tp3_rag_sources/` | Implémenter un seuil de refus et vérifier les extraits cités dans les chunks |
| `tp4_evaluation/` | Implémenter deux métriques et comparer trois versions du RAG avec quatre métriques inspirées de RAGAS |
| `demos/demo4_gradio_assistant/` | Assembler les capacités dans une interface Gradio activable par options |

## Le code partagé

`code_partage/`, aussi utilisé par les modules 3 à 5 pour la recherche documentaire :

| Fichier | Contenu |
|---|---|
| `rag.py` | chargement (PDF, HTML, Word, scan), nettoyage, chunking, embeddings, recherche avec filtre de date, reranking, prompt, génération |
| `rag_advanced.py` | réécriture, multi-requête, HyDE, BM25, fusion RRF, mesure du MRR, réponse avec citations vérifiées, juge |
| `weaviate_store.py` | base vectorielle : Weaviate (cloud ou local), ou une base en mémoire si Weaviate est injoignable |
| `config.py` | charge `.env` et vérifie la connexion aux modèles |
| `front.py` | thème et blocs de l'interface Gradio |

Les questions de mesure sont dans `data/evaluation/questions_rag.json` : 12 cas courants et 35 cas difficiles (fautes, anglais, nombres exacts, suites de conversation).

## Prérequis

- `.env` : `LLM_API_KEY`, `MODELE`, `MODELE_EMBEDDING`, et pour le reranking (TP2 et suivants) `MODELE_RERANK`, `RERANK_API_KEY`, `RERANK_API_BASE` (voir `.env.example`).
- Weaviate : `docker compose up -d` à la racine du dépôt. Sans Docker, une base en mémoire prend le relais.
- Le reranker est partagé par la salle et limité en débit : 15 questions au TP2, une vingtaine au TP4.
