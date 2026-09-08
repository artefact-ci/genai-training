# GenAI Training

Formation de 5 jours sur l'IA générative appliquée, des fondamentaux jusqu'à un système
conversationnel de qualité production.

- **Public** : développeurs et data scientists, à l'aise en Python.
- **Format** : 5 jours, environ 40 % d'exposé et 60 % de travaux pratiques.
- **Langue** : supports en français, code et commentaires en anglais.
- **Fil rouge** : un assistant de support client e-commerce, construit incrémentalement
  d'un chapitre à l'autre. Voir [fil-rouge/](fil-rouge/README.md).

## Programme

| # | Chapitre | Contenu |
|---|---|---|
| 0 | Environnement & harness agentique | Développement assisté par agent avec Claude Code : boucle agentique, contexte, permissions, extensions. |
| 1 | Fondamentaux GenAI & prompt engineering | LLM, tokens, embeddings, fenêtre de contexte ; techniques de prompting ; sorties structurées ; coût, latence et choix de modèle. |
| 2 | Évaluer un système GenAI | Jeux de test, métriques, LLM-as-judge, détection de régression. |
| 3 | RAG & données métier | Ingestion, découpage, embeddings, bases vectorielles, évaluation de la recherche. |
| 4 | Agents & orchestration | Tool calling, boucle de raisonnement, orchestration multi-étapes avec LangGraph, agentic RAG. |
| 5 | Conception conversationnelle | Design de dialogue, mémoire, gestion des impasses, tests de flux. |
| 6 | Intégration multicanale, sécurité & gouvernance | Canaux, authentification, injection de prompt, confidentialité, observabilité. |

## Déroulé sur 5 jours

| Jour | Matin | Après-midi |
|---|---|---|
| J1 | Ch. 0 Harness (2 h) puis Ch. 1 Fondamentaux | Ch. 1 Fondamentaux — prompt engineering, labs |
| J2 | Ch. 1 fin — sorties structurées, coût et choix de modèle | Ch. 2 Évaluation |
| J3 | Ch. 3 RAG — ingestion, découpage, embeddings | Ch. 3 RAG — lab complet et évaluation de la recherche |
| J4 | Ch. 4 Agents — tool calling, boucle de raisonnement | Ch. 4 Agents — orchestration LangGraph, agentic RAG |
| J5 | Ch. 5 Conception conversationnelle | Ch. 6 Multicanal, sécurité, gouvernance et restitution du fil rouge |

Les chapitres sont préparés et livrés dans l'ordre, une pull request chacun.

## Structure du dépôt

```
chapitres/NN-nom/
  README.md      objectifs, prérequis, déroulé horaire du chapitre
  cours.md       le contenu rédigé, autoportant, pour travailler en autonomie
  slides.md      le support projeté en présentiel (Marp)
  quiz.md        vérification des acquis
  labs/          travaux pratiques, chacun avec starter/ et solution/
commun/
  llm/           accès au modèle, partagé par tous les labs
  setup/         installation de l'environnement
fil-rouge/       énoncé et données du cas fil rouge
```

Chaque chapitre se lit de deux façons : `cours.md` pour un participant seul, `slides.md`
pour une session animée. `cours.md` fait foi ; les slides en sont une projection synthétique.

## Démarrer

Les dépendances sont gérées avec [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp commun/setup/.env.example .env
```

Renseigner ensuite les accès au modèle dans `.env`, puis vérifier :

```bash
uv run python commun/setup/check_env.py
```

Le détail, y compris sous Windows et en cas de problème, est dans
[commun/setup/README.md](commun/setup/README.md).

## Contribuer

Les conventions d'écriture et le processus de relecture sont décrits dans
[CONTRIBUTING.md](CONTRIBUTING.md). L'avancement chapitre par chapitre est suivi dans
[TODO.md](TODO.md).
