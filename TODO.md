# TODO

Avancement de la préparation, chapitre par chapitre. Chaque chapitre est livré en une PR
contenant `README.md`, `cours.md`, `slides.md`, `quiz.md` et au moins un lab.

## Socle

- [x] Définir la structure du dépôt et les conventions (`CONTRIBUTING.md`)
- [x] Poser le template de chapitre (`chapitres/_template/`)
- [x] Écrire l'abstraction d'accès au modèle (`commun/llm/`)
- [x] Écrire le guide d'installation (`commun/setup/`)
- [x] Définir la durée et le découpage en 5 jours
- [x] Choisir le cas fil rouge
- [ ] Produire le jeu de données du fil rouge (avant le chapitre 3)
- [ ] Définir les critères d'évaluation des participants
- [ ] Mettre en place le questionnaire de satisfaction

## 0. Environnement & harness agentique

- [ ] Objectifs et prérequis
- [ ] Boucle agentique : ce qu'un harness ajoute à un LLM
- [ ] Contexte : ce qui l'occupe, comment le piloter
- [ ] Contexte projet et configuration (`CLAUDE.md`, `settings.json`, permissions)
- [ ] Extensions : commandes, compétences, sous-agents, hooks, MCP
- [ ] Lab guidé — configurer le dépôt de formation
- [ ] Slides
- [ ] Quiz

## 1. Fondamentaux — GenAI & prompt engineering

- [ ] Objectifs et prérequis
- [ ] Concepts : LLM, tokens, embeddings, fenêtre de contexte, échantillonnage
- [ ] Techniques de prompting : zero-shot, few-shot, chaîne de pensée, prompt système
- [ ] Sorties structurées et validation
- [ ] Coût, latence et choix de modèle
- [ ] Labs : conception et itération de prompts
- [ ] Slides
- [ ] Quiz
- [ ] Fil rouge : première réponse de l'assistant support

## 2. Évaluer un système GenAI

- [ ] Objectifs et prérequis
- [ ] Construire un jeu de test représentatif
- [ ] Métriques : exactitude, fidélité, pertinence, coût, latence
- [ ] LLM-as-judge : mise en œuvre et limites
- [ ] Détection de régression et intégration continue
- [ ] Lab : harnais d'évaluation réutilisable pour les chapitres suivants
- [ ] Slides
- [ ] Quiz
- [ ] Fil rouge : jeu de test de l'assistant support

## 3. RAG & données métier

- [ ] Objectifs et prérequis
- [ ] Architecture RAG : indexation, recherche, génération
- [ ] Ingestion et stratégies de découpage
- [ ] Embeddings et bases vectorielles
- [ ] Recherche hybride et reclassement
- [ ] Évaluation de la recherche et de la fidélité des réponses
- [ ] Pièges : données périmées, découpage inadapté, bruit de recherche
- [ ] Lab : RAG complet sur les données du fil rouge
- [ ] Slides
- [ ] Quiz

## 4. Agents & orchestration

- [ ] Objectifs et prérequis
- [ ] Concepts : outils, boucle de raisonnement, planification, arrêt
- [ ] Tool calling et définition de fonctions
- [ ] Orchestration multi-étapes et multi-agents avec LangGraph
- [ ] Agentic RAG
- [ ] Ce qui est propre au framework et ce qui ne l'est pas
- [ ] Débogage et observabilité d'un agent
- [ ] Lab : agent outillé sur les API du fil rouge
- [ ] Slides
- [ ] Quiz

## 5. Conception conversationnelle

- [ ] Objectifs et prérequis
- [ ] Design de dialogue : tours, contexte, mémoire
- [ ] Flux de conversation, impasses et passage à un humain
- [ ] Ergonomie des interfaces conversationnelles
- [ ] Tests de flux : cas nominal et cas limites
- [ ] Lab : conception et test des flux du fil rouge
- [ ] Slides
- [ ] Quiz

## 6. Intégration multicanale, sécurité & gouvernance

- [ ] Objectifs et prérequis
- [ ] Schémas d'intégration par canal (web, Slack, Teams, voix)
- [ ] Authentification et contrôle d'accès
- [ ] Sécurité : injection de prompt, exfiltration, périmètre des outils
- [ ] Gouvernance : confidentialité, conformité, traçabilité
- [ ] Supervision et observabilité en production
- [ ] Schéma d'architecture de référence
- [ ] Lab : démonstration d'attaque et mise en défense
- [ ] Slides
- [ ] Quiz
