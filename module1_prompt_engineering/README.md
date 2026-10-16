# Module 1 – Prompt engineering pour développeurs : TP 1 et TP 2

Fil rouge : l'assistant support client d'**Orange Bank** (cadrage, §2–§5).
Toutes les données sont **fictives** et ne reflètent pas les procédures d'Orange Bank.
La base est celle de la formation (`banque.db`, dossier « Orange Bank - GenAI Training »).
Date de référence des données : **lundi 16 novembre 2026**.

## Contenu

```
data/
  construire_messages.py     → messages_clients.jsonl : 30 messages clients + sortie attendue (M1, M3)
  banque.db                  base SQLite de la formation (copie de la version du 16/10/2026)
tp1_extraction/
  evaluation.py              notation commune (fournie)
  squelette/                 à compléter par les participants (5 TODO, dont 1 bonus)
  solution/                  prompt v1, schéma Pydantic, script complet
tp2_function_calling/
  squelette/                 à compléter (4 TODO)
  solution/                  get_schedule + boucle d'appel de fonction écrite à la main
verifier_env.py              vérification de l'environnement
.env.example                 modèles et clés API
```

Pour le dépôt Git (« une branche par jour ») : les dossiers `squelette/` vont sur la branche
de départ du jour 1, les dossiers `solution/` sur la branche de solution.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env              # puis renseigner les clés et les modèles
python verifier_env.py --ping
```

Le fournisseur de LLM n'est pas encore décidé (cadrage, §13). Les TP passent par **LiteLLM** :
le même code appelle OpenAI, Anthropic, Mistral, Gemini ou un modèle local (Ollama) ;
seul le nom du modèle change dans `.env`.

---

## TP 1 – Extraire un message client en JSON et comparer trois modèles

**Objectif.** Transformer un message libre en JSON exploitable par le code. Ce format est
réutilisé tel quel par le routeur de l'agent au module 3, qui aiguille sur `categorie`.

**Schéma de sortie**

| Champ | Valeurs | Noté automatiquement |
|---|---|---|
| `categorie` | `P1` question produit/frais · `P2` échéance · `P3` anomalie de remboursement · `P4` hors périmètre · `P5` fraude | oui |
| `produit` | `pret` · `epargne` · `orange_money` · `autre` | oui |
| `motif` | résumé en une phrase | non (référence fournie) |
| `dates` | liste `AAAA-MM-JJ` (dates relatives converties) | oui |
| `montants_fcfa` | liste d'entiers | oui |
| `urgence` | `basse` · `moyenne` · `haute` | oui |
| `sentiment` | `satisfait` · `neutre` · `inquiet` · `mecontent` | oui |

**Jeu de test** (`data/messages_clients.jsonl`) : 30 messages, 7 P1, 6 P2, 7 P3, 6 P4 et 4 P5,
couvrant les cinq personas du cadrage, avec des messages abrégés (Aminata), du français ivoirien
courant (MSG-16, MSG-29) et une tentative d'injection (MSG-23).

**Déroulé (45 min environ)**
1. Écrire le prompt dans `prompt_extraction_v1.txt` (TODO 1).
2. Compléter `extraire_json`, `appeler` et `analyser` (TODO 2 à 4). Tester sur `--limite 3`.
3. Lancer sur les 30 messages avec les trois modèles de `MODELES_TP1`.
4. Remplir le tableau livrable : JSON valide /30, champs justes /180, latence moyenne, coût pour 1 000 messages.
5. Conclure en une phrase : quel modèle pour l'assistant, et pourquoi.
6. **Bonus** : compléter `schema.py` (TODO 5), comparer `--mode prompt` et `--mode structure`.

```bash
python tp1_extraction/squelette/tp1_extraction.py --limite 3
python tp1_extraction/solution/tp1_extraction.py
python tp1_extraction/solution/tp1_extraction.py --mode structure
```
Le détail par message est écrit dans `resultats/tp1_details_<mode>.csv`.

**Points à discuter en débrief**
- Les erreurs de catégorie listées en fin d'exécution : P1/P4 (question sur les conditions ou demande
  de décision ?) et P3/P5 sont les frontières les plus fines.
- MSG-23 (injection) : un bon extracteur classe le message en P4 au lieu d'y obéir.
- L'urgence et le sentiment varient d'un modèle à l'autre si le prompt ne donne pas de règle :
  c'est l'occasion de faire une v2 du prompt et de la rejouer sur le même jeu (« un prompt se versionne »).
- Le coût est estimé par LiteLLM à partir de sa grille de prix ; un modèle local affiche « n/d ».

---

## TP 2 – Écrire un premier appel de fonction sans framework

**Objectif.** Manipuler à la main le cycle du function calling avant de le retrouver encapsulé
dans LangChain au module 3. Parcours **P2** du cadrage : « Quand est ma prochaine échéance ? »

**L'outil.** `get_schedule(client_id, pret_id=None)` lit les tables `prets` et `echeances` de `banque.db`.
`client_id` **n'est pas un paramètre exposé au modèle** : il vient de la session (client identifié
par l'application). Le modèle ne peut donc pas demander l'échéancier d'un tiers : c'est le premier
garde-fou du secret bancaire, avant même le prompt.

**Déroulé (45 min environ)**
1. Compléter la requête des échéances dans `get_schedule` (TODO 1).
2. Écrire la description de l'outil (TODO 2) : c'est elle qui décide si le modèle l'appelle.
3. Compléter la boucle : renvoyer le message du modèle, exécuter la fonction, renvoyer le résultat (TODO 3 et 4).
4. Passer les quatre scénarios de test.

```bash
python tp2_function_calling/squelette/tp2_get_schedule.py
python tp2_function_calling/solution/tp2_get_schedule.py --client CLI-0002 --question "Il me reste combien à payer ?"
```

| Client | Question | Comportement attendu |
|---|---|---|
| CLI-0001 (Aminata) | Quand est ma prochaine échéance ? | 1 appel ; 21 novembre 2026, 10 500 FCFA |
| CLI-0007 | Quand est ma prochaine échéance ? | 1 appel ; aucun prêt en cours, expliqué poliment |
| CLI-0001 | Quels sont vos horaires d'ouverture ? | aucun appel d'outil |
| CLI-0001 | Et la prochaine échéance de mon frère ? (CLI-0002) | refus ; aucune donnée de CLI-0002 |

Pour aller plus loin : CLI-0002 (M. Kouassi) a une échéance impayée ; l'assistant doit la signaler
et proposer un conseiller, sans diagnostiquer : le diagnostic, c'est l'agent P3 du module 3.

---

## banque.db : cas utilisés

| Client | Situation | Utilisé par |
|---|---|---|
| CLI-0001, Aminata | Prêt Express en cours, échéance le 21/11/2026 (10 500 FCFA) | TP 2 |
| CLI-0002, M. Kouassi | Remboursement du 15/11 réussi mais non rattaché (incident INC-0005), échéance impayée | TP 2 « pour aller plus loin », module 3 |
| CLI-0007 | Aucun prêt en cours | TP 2 |

Les 30 messages du TP 1 sont alignés sur les produits (Prêt Express, Prêt Express+, Épargne Plus), les frais (retard : 2 000 / 5 000 FCFA) et la date de référence de `banque.db`.
