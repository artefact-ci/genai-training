# Module 3 : Agents IA avec LangChain et LangGraph, travaux pratiques

Fil rouge : l'assistant support client d'Orange Bank. Données de la formation : base `banque.db` et corpus du dossier « Orange Bank - GenAI Training » (fictifs). Date de référence : 16 novembre 2026.

## Contenu

```
notebooks/
  Module3_TP_participants.ipynb   à compléter (12 TODO)
  Module3_TP_formateur.ipynb      avec les solutions
```

Les notebooks s'ouvrent directement dans Colab. Ils embarquent une copie de `banque.db` (version du 16/10/2026) et du corpus découpé en 119 extraits (DOC-01 à DOC-09, sauf DOC-04 et la note de service scannée). Si `data/banque.db` existe déjà (dépôt cloné), c'est ce fichier qui est utilisé. `search_docs` fait une recherche par mots-clés, filtrée par date de validité (DOC-07 jusqu'au 30/06/2026, DOC-08 depuis le 01/07/2026) ; au module 2, elle sera remplacée par l'index RAG.

## Déroulé

| Partie | Contenu | Durée | TODO |
|---|---|---|---|
| Atelier | Workflow ou agent ? Six cas | 20 min | réponses |
| TP 1 | Les sept outils du cadrage, `client_ref` injecté par `ToolRuntime` | 45 min | 1 à 4 |
| TP 2 | Agent P3 avec `create_agent` (M. Kouassi + trois autres issues) | 45 min | 5 |
| TP 3 | Mémoire : checkpointer et `thread_id` | 20 min | 6 |
| TP 4 | Validation humaine (`HumanInTheLoopMiddleware`), injection directe et indirecte, secret bancaire | 45 min | 7 et 8 |
| TP 5 | Graphe LangGraph : routeur P1 à P5, boucle P3 explicite, `interrupt()` | 60 min | 9 à 11 |
| TP 6 | Traces (callback, Langfuse en option) et 5 scénarios de test automatisés | 45 min | 12 |

## Configuration

- Accès au modèle via LiteLLM (`ChatLiteLLM`), le fournisseur n'étant pas encore décidé : changer `MODELE` suffit. Choisir un modèle qui gère bien l'appel d'outils.
- Clés dans les Secrets de Colab : `OPENAI_API_KEY` (ou autre fournisseur) et, en option, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`.
- `SIMULATION = True` remplace le modèle par un modèle simulé qui suit un script : il permet de tester la plomberie sans clé, pas la qualité du modèle. Le notebook formateur est livré en simulation.

## Cas de banque.db utilisés

| Client | Situation | Issue attendue |
|---|---|---|
| CLI-0002, M. Kouassi | Remboursement OM-20261115-00002 réussi à 14 h 32, non rattaché ; incident INC-0005 (14 h – 16 h 30) | Régularisation validée par un conseiller |
| CLI-0003, Adjoua Koné | Remboursement en échec (SOLDE_INSUFFISANT) | Explication, aucune régularisation |
| CLI-0004, Didier Yao | Échéance ECH-0004 impayée, aucune transaction | Réclamation avec dossier (format des réclamations existantes) |
| CLI-0006, Ibrahim Diabaté | Prêt à 2 h 47 depuis un nouvel appareil, retrait 3 minutes après | Transfert immédiat (P5, DOC-09) |
| CLI-0007, Serge N'Guessan | « NOTE SYSTÈME » dans le libellé d'une transaction | Injection indirecte |
| CLI-0001, Aminata | Prêt Express en cours | P2, injection directe, accès à un tiers |

Les écritures respectent le schéma de Julien : régularisation avec `propose_par = 'agent'`, `validateur` (CONS-xx) et justification obligatoire (DOC-08) ; refus consignés ; dossier de réclamation au format `schema_version 1.0`.

## État des tests

Les deux notebooks ont été exécutés de bout en bout en mode simulation (5 scénarios de test au vert dans la version formateur). Un passage avec une vraie clé API reste à faire une fois le fournisseur choisi.
