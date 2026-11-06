# Démo : un message WhatsApp de bout en bout

## Trajet d'un message

1. Le client écrit sur WhatsApp. Meta envoie un webhook HTTPS à votre service.
2. `service/channels/whatsapp.py` vérifie la signature, marque le message comme lu et répond 200 immédiatement.
3. `socle/gateway.py` écarte les doublons, limite le débit, identifie le client et traite un message à la fois par utilisateur.
4. `socle/assistant.py` exécute l'agent : classement, tools, garde-fous. La régularisation attend la validation d'un conseiller.
5. L'adaptateur renvoie la réponse par l'API Graph, dans la fenêtre de 24 heures.

| Fichier | Rôle |
|---|---|
| `service/channels/whatsapp.py` | Webhook, signature, envoi |
| `socle/gateway.py` | Doublons, limite de débit, identification, commandes |
| `socle/assistant.py` | Agent LangGraph, garde-fous, reprise après validation |
| `service/service.py` | Application FastAPI, interface conseiller |

## Préparation

1. Créez une application sur Meta for Developers avec le produit WhatsApp. Dans *API Setup*, relevez :
   - l'identifiant du numéro : `WA_PHONE_NUMBER_ID` ;
   - le token d'accès : `WA_TOKEN`. Le token temporaire affiché dans la console expire après 24 heures.
     Pour une démo planifiée, créez un token permanent avec un utilisateur système.
2. Ajoutez votre numéro à la liste des destinataires de test : en mode développement, WhatsApp n'envoie qu'à ces numéros.
3. Renseignez dans `.env` :
   - `WA_TOKEN`, `WA_PHONE_NUMBER_ID` : valeurs de l'étape 1.
   - `WA_VERIFY_TOKEN` : une chaîne de votre choix. Vous la saisirez aussi dans Meta.
   - `META_APP_SECRET` : *App settings > Basic*. Il sert à vérifier la signature des webhooks.
   - `CLIENT_PAR_DEFAUT=CLI-0002` : tout numéro qui écrit au bot est traité comme ce client. Pour rattacher des numéros précis à des clients différents, utilisez `IDENTITES={"<numéro sans +>": "CLI-0002"}`.
   - `LLM_API_KEY` et `MODELE` : le modèle de l'agent.
4. Facultatif : renseignez les clés Langfuse (voir le `README.md` racine).
5. Lancez le service : `cd 05_canaux_gouvernance/service && uv run uvicorn service:app --port 8000`.
6. Exposez le port : `ngrok http 8000`. L'URL gratuite peut changer à chaque lancement : mettez alors à jour le webhook dans Meta.
   > Attention : le tunnel rend tout le service public, y compris `/conseiller` qui n'a pas d'authentification. Coupez-le en fin de session et n'utilisez que des données fictives.
7. Dans Meta, ouvrez *WhatsApp > Configuration* et renseignez :
   - l'URL de rappel `https://<tunnel>/webhook/whatsapp` ;
   - le token de vérification, identique à `WA_VERIFY_TOKEN` ;
   - l'abonnement au champ `messages`.

Vérifiez la préparation :

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=<WA_VERIFY_TOKEN>&hub.challenge=42"
```

`/health` liste `whatsapp` parmi les canaux. La seconde commande renvoie `42`.

## Déroulé

1. Écrivez au bot depuis votre téléphone : « J'ai remboursé hier, mais mon dossier indique un impayé ».
2. Suivez la requête dans les logs du service, puis dans l'interface ngrok (`http://localhost:4040`).
3. Ouvrez la trace dans Langfuse : session, tools appelés, latence et coût de la conversation.
4. Validez la régularisation sur `http://localhost:8000/conseiller`. La suite de la conversation arrive sur le téléphone.
5. Écrivez « Je veux parler à un conseiller ». Le dossier apparaît dans l'espace conseiller avec les derniers messages.
   Cliquez sur *Prendre en charge* : l'assistant se retire, vos messages partent sur le téléphone et les réponses du client
   arrivent dans la page. *Clore et rendre la main à l'assistant* termine l'échange.
