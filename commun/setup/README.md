# Installation de l'environnement

À faire **avant** le premier jour. Compter une vingtaine de minutes, dont l'essentiel en
attente de téléchargements.

## Prérequis

- Python 3.11 ou plus récent
- Git
- Un accès Azure OpenAI (fourni par l'organisateur) : point de terminaison, clé, et le nom
  des déploiements

## 1. Récupérer le dépôt et créer l'environnement

```bash
git clone https://github.com/artefact-ci/genai-training.git
cd genai-training
python -m venv .venv
```

Activer l'environnement — sous macOS et Linux :

```bash
source .venv/bin/activate
```

Sous Windows, en PowerShell :

```powershell
.venv\Scripts\Activate.ps1
```

## 2. Installer les dépendances

```bash
pip install -r commun/setup/requirements.txt
```

```bash
pip install -e .
```

Le second `pip install` installe le dépôt lui-même en mode éditable. C'est ce qui permet à
un lab situé dans `chapitres/03-rag/labs/01-.../` d'écrire simplement
`from commun.llm import chat`, sans manipuler `sys.path`.

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
python commun/setup/check_env.py
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

## Problèmes courants

| Symptôme | Cause probable |
|---|---|
| `Cannot import commun.llm` | `pip install -e .` n'a pas été lancé, ou l'environnement virtuel n'est pas activé |
| `Missing environment variable AZURE_OPENAI_API_KEY` | `.env` est absent, ou placé ailleurs qu'à la racine du dépôt |
| `DeploymentNotFound` | La variable contient le nom du modèle au lieu du nom du déploiement |
| `401` ou `403` | Clé erronée, ou clé ne correspondant pas au point de terminaison renseigné |
| Le script fonctionne mais un lab du chapitre 3 échoue | `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` n'est pas renseigné |

## Changer de fournisseur

Les labs n'appellent jamais un SDK de fournisseur directement : ils passent par
`commun/llm`. Basculer vers un autre fournisseur consiste donc à implémenter le client
correspondant dans `commun/llm/client.py` et à ajuster `.env` — les exercices, eux, ne
changent pas.
