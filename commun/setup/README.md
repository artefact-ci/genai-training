# Installation de l'environnement

À faire **avant** le premier jour. Compter une vingtaine de minutes, dont l'essentiel en
attente de téléchargements.

## Prérequis

- [uv](https://docs.astral.sh/uv/) — gestionnaire de dépendances et d'environnements Python
- Git
- Un accès Azure OpenAI (fourni par l'organisateur) : point de terminaison, clé, et le nom
  des déploiements

Python n'est pas un prérequis séparé : `uv` installe lui-même la version attendue par le
dépôt (3.11 ou plus récent).

### Installer uv

Sous macOS et Linux :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sous Windows, en PowerShell :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Avec Homebrew, si vous préférez :

```bash
brew install uv
```

## 1. Récupérer le dépôt

```bash
git clone https://github.com/artefact-ci/genai-training.git
cd genai-training
```

## 2. Installer les dépendances

```bash
uv sync
```

Cette commande fait tout : elle installe la bonne version de Python si nécessaire, crée
l'environnement virtuel dans `.venv`, installe les dépendances aux versions exactes de
`uv.lock`, et installe le dépôt lui-même en mode éditable. C'est ce dernier point qui
permet à un lab situé dans `chapitres/03-rag/labs/01-.../` d'écrire simplement
`from commun.llm import chat`, sans manipuler `sys.path`.

Comme les versions sont figées par `uv.lock`, tous les participants travaillent sur le
même environnement — ce qui évite les écarts inexplicables entre deux postes en séance.

## 3. Renseigner les accès au modèle

```bash
cp commun/setup/.env.example .env
```

Ouvrir `.env` et remplir les valeurs communiquées par l'organisateur. Attention à un point
qui piège souvent : `AZURE_OPENAI_CHAT_DEPLOYMENT` attend le **nom du déploiement** créé
dans le portail Azure, qui n'est pas forcément le nom du modèle.

`.env` est ignoré par Git. Aucune clé ne doit être commitée, ni collée dans un lab, ni
transmise dans un canal de discussion.

## 4. Vérifier

```bash
uv run python commun/setup/check_env.py
```

Le script contrôle la version de Python, l'installation du dépôt, les variables
d'environnement, puis effectue un appel réel au modèle. Il affiche tous les problèmes
rencontrés d'un coup, avec le moyen de les corriger.

Sortie attendue :

```
[ok]   Python version
[ok]   Repository installed
[ok]   Environment variables
  model      : gpt-4o-2024-08-06
  answer     : 'OK'
  tokens     : 23
[ok]   Model reachable

Environment ready.
```

## Travailler au quotidien

Préfixer les commandes par `uv run` suffit : il n'y a pas d'environnement à activer à la
main, et `uv` se charge de le synchroniser si le `pyproject.toml` a changé.

```bash
uv run python chapitres/01-fondamentaux/labs/01-prompting/starter/main.py
```

```bash
uv run pytest
```

Ceux qui préfèrent l'activation explicite peuvent le faire — `source .venv/bin/activate`,
ou `.venv\Scripts\Activate.ps1` sous Windows — mais ce n'est pas nécessaire.

## Problèmes courants

| Symptôme | Cause probable |
|---|---|
| `uv: command not found` | uv n'est pas installé, ou le terminal n'a pas été rouvert depuis son installation |
| `Cannot import commun.llm` | La commande a été lancée sans `uv run`, avec le Python du système |
| `Missing environment variable AZURE_OPENAI_API_KEY` | `.env` est absent, ou placé ailleurs qu'à la racine du dépôt |
| `DeploymentNotFound` | La variable contient le nom du modèle au lieu du nom du déploiement |
| `401` ou `403` | Clé erronée, ou clé ne correspondant pas au point de terminaison renseigné |
| Le script fonctionne mais un lab du chapitre 3 échoue | `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` n'est pas renseigné |

## Changer de fournisseur

Les labs n'appellent jamais un SDK de fournisseur directement : ils passent par
`commun/llm`. Basculer vers un autre fournisseur consiste donc à implémenter le client
correspondant dans `commun/llm/client.py` et à ajuster `.env` — les exercices, eux, ne
changent pas.
