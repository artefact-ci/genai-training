# GenAI Training

Le programme de formation couvre les fondamentaux et l'application pratique de la GenAI, des concepts fondamentaux aux systèmes conversationnels prêts pour la mise en production.

## Plan du programme

### 1. Fondamentaux — GenAI & Prompt Engineering
Concepts fondamentaux de la GenAI et des Large Language Models (LLM), ainsi que les techniques de prompt engineering pour concevoir des prompts efficaces et fiables.

### 2. AI Agents avec LangChain / LangGraph
Construction d'agents autonomes et semi-autonomes en utilisant LangChain et LangGraph, couvrant l'utilisation d'outils, l'orchestration et les workflows de raisonnement multi-étapes.

### 3. RAG & Business Data
Techniques de Retrieval-Augmented Generation (RAG) pour contextualiser les modèles avec des données métier, améliorant la précision et la pertinence des résultats générés.

### 4. Conception de Bots Conversationnels
Principes et bonnes pratiques pour concevoir des chatbots, y compris la conception du dialogue, la gestion du contexte l'expérience utilisateur.

### 5. Intégration Multicanal & Gouvernance
Déploiement de chatbots et agents IA sur de multiples canaux en traitant les questions de gouvernance, conformité et l'opérationnel.

### 6. Harness
Prise en main du harness Claude Code et de son écosystème d'outils pour créer des workflows de dev agentiques.

## Statut

Ce dépôt est en développement actif. Le contenu et les matériaux pour chaque module seront ajoutés progressivement.

## Usage formateur

Ce dépôt contient la formation « Agents IA & AI Engineering » ; le fil rouge est un assistant
support client pour Lagune Banque (données fictives). La seule branche durable est `main` :
chaque module est ajouté sur sa propre branche, puis fusionné.

### Les deux dossiers

- `starter/` : ce que les participants clonent (sparse checkout). Projet `uv` (Python 3.11),
  démos, TP et code de départ.
- `solutions/` : réservé au formateur (solutions des TP, scripts de contrôle).
  Les participants ne le récupèrent pas.

### Règle de nommage

Le notebook participant `mN/…/tpN.ipynb` de `starter/` a son équivalent `tpN_solution.ipynb`
dans `solutions/mN/` (ex. `starter/m1/tp1_extraction_json/tp1.ipynb` ↔
`solutions/m1/tp1_solution.ipynb`).

### Vérifier les notebooks (la veille de la formation)

Depuis `starter/` :

```bash
uv sync
uv run python ../solutions/scripts/check_notebooks.py
```

Le script exécute chaque notebook de `solutions/` et de `starter/*/demos/` dans un dossier
temporaire (les fichiers ne sont pas modifiés), affiche un tableau OK / ÉCHEC et retourne un
code d'erreur si l'un échoue. À lancer **la veille** de la formation.

### Règle d'autonomie des modules

Chaque dossier `starter/mN/` doit être **autonome** : il contient le code de départ du module
(par exemple l'index RAG et les outils du module 2 dans `m3/`). Ainsi, un binôme en retard
repart du module suivant sans dépendre de ce qui devait être fait la veille.
