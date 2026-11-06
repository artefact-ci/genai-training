# Module 4 : Interopérabilité avec MCP et A2A

| Dossier | Description |
|---|---|
| `demos/demo1_fastmcp/` | Créer un serveur FastMCP, découvrir ses outils depuis un client, puis les utiliser avec l'agent |
| `demos/demo2_injection/` | Observer l'effet d'une description d'outil MCP malveillante et les contrôles côté hôte |
| `tp1_mcp_prets/` | Implémenter un serveur en lecture seule, le tester en stdio et en HTTP, puis y connecter l'agent |
| `demos/demo3_a2a/` | Présenter une Agent Card A2A pour un agent de détection de fraude |

## Le socle

| Fichier | Contenu |
|---|---|
| `socle/loans.py` | accès aux prêts et à la documentation, utilisé par le serveur MCP |
| `socle/mcp_bridge.py` | adaptation des outils MCP au format LangChain |

## Prérequis

- `.env` : `LLM_API_KEY`, `MODELE` et `MODELE_EMBEDDING` (pour `search_docs`).
