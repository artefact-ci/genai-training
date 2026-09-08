# Conventions de contribution

## Une PR par chapitre

Chaque chapitre est préparé sur une branche `chapitre/NN-nom` et livré en une pull request.
Une PR de chapitre est complète quand elle contient :

- `README.md` — objectifs pédagogiques, prérequis, déroulé horaire
- `cours.md` — le contenu rédigé
- `slides.md` — le support présentiel
- `quiz.md` — au moins six questions de vérification
- `labs/` — au moins un lab avec `starter/` et `solution/`
- les cases correspondantes cochées dans `TODO.md`
- les dépendances Python du chapitre ajoutées avec `uv add`

Le chapitre `_template/` sert de point de départ : le copier, ne pas le modifier sans
raison, puisqu'il fixe le format commun.

## `cours.md` fait foi

Le risque principal de ce format à deux supports est la divergence entre le cours rédigé
et les slides. La règle est donc :

- `cours.md` contient l'intégralité du propos, rédigé en phrases complètes. Un participant
  qui suit la formation en autonomie doit pouvoir s'en sortir avec ce seul fichier, sans
  l'animation orale.
- `slides.md` est une projection : titres, schémas, extraits de code, points saillants.
  Aucune information ne doit exister uniquement dans les slides.
- Les titres de niveau 2 de `slides.md` reprennent ceux de `cours.md`, pour qu'on puisse
  passer de l'un à l'autre pendant l'animation.

Quand une correction touche le fond, elle est portée dans `cours.md` puis répercutée dans
`slides.md` — jamais l'inverse.

## Écriture

- Supports (`README.md`, `cours.md`, `slides.md`, `quiz.md`) en français.
- Code, noms de variables, commentaires et messages de commit en anglais.
- Une ligne par phrase n'est pas exigée, mais on retourne à la ligne autour de 100
  caractères pour que les diffs restent lisibles en relecture.
- Les captures et schémas vont dans `chapitres/NN-nom/assets/`.

## Slides

Les slides sont écrites en Markdown au format [Marp](https://marp.app/), pour qu'une PR
reste relisible — un binaire PowerPoint ne se relit pas. Prévisualisation et export :

```bash
npx @marp-team/marp-cli@latest chapitres/_template/slides.md --html --preview
```

```bash
npx @marp-team/marp-cli@latest chapitres/_template/slides.md --pdf --allow-local-files
```

Les exports (`*.pdf`) ne sont pas versionnés.

## Labs

Chaque lab est un dossier `labs/NN-nom/` contenant :

- `README.md` — énoncé, durée visée, critères de réussite
- `starter/` — le code remis aux participants, avec des `TODO` explicites
- `solution/` — la version de référence, exécutable telle quelle

Un lab doit tourner sur un poste neuf après le seul `commun/setup`. Les labs n'importent
jamais un SDK de fournisseur directement : ils passent par `commun.llm` (voir ci-dessous).

## Dépendances

Les dépendances sont gérées avec [uv](https://docs.astral.sh/uv/). `pyproject.toml` en est
la seule source de vérité et `uv.lock` est versionné, pour que tous les participants
travaillent sur les mêmes versions.

Une dépendance s'ajoute avec `uv add`, jamais en éditant `pyproject.toml` à la main — sans
quoi le lock se désynchronise :

```bash
uv add langgraph
```

```bash
uv add --dev pytest-cov
```

Une PR de chapitre ajoute ses dépendances à `[project.dependencies]`, sans les isoler dans
un extra : les participants doivent obtenir la totalité de l'environnement en un seul
`uv sync` le premier jour, plutôt que de découvrir une installation manquante au troisième.

Le lock modifié fait partie du diff, et sa mise à jour est vérifiée en relecture.

## Tests

Les tests sont écrits avec `pytest`, et se lancent depuis la racine :

```bash
uv run pytest
```

Ce qu'on attend d'une PR de chapitre :

- le code partagé (`commun/`) est testé ; ses tests vivent à côté de lui, en
  `test_<module>.py` ;
- la solution de chaque lab est couverte par au moins un test qui vérifie qu'elle produit
  le résultat annoncé — c'est ce qui empêche une solution de pourrir silencieusement entre
  deux sessions ;
- les tests tournent sans réseau et sans credentials. Les appels au modèle sont simulés,
  hors du script de vérification d'environnement qui, lui, appelle réellement le modèle
  puisque c'est son objet.

Un test qui exige un accès au modèle est marqué `@pytest.mark.live` et exclu par défaut.

## Accès au modèle

Le fournisseur de modèle n'est pas figé. Tout le code passe donc par `commun/llm`, qui
lit sa configuration dans `.env`. Changer de fournisseur doit rester un changement de
configuration, jamais une réécriture des labs.

```python
from commun.llm import chat

chat([{"role": "user", "content": "Bonjour"}])
```

Quand un lab a besoin d'une fonctionnalité propre à un fournisseur, elle est isolée et
signalée par un encart explicite dans `cours.md`.

## Fil rouge

Le cas fil rouge — un assistant de support client e-commerce — est décrit dans
`fil-rouge/`. Chaque chapitre lui ajoute une brique. Un lab qui n'a rien à voir avec le
fil rouge est acceptable, mais chaque chapitre doit en faire progresser au moins un.

## Relecture

Une PR de chapitre est relue sur trois points : la justesse technique, la faisabilité du
lab dans le temps annoncé, et la cohérence entre `cours.md` et `slides.md`.
