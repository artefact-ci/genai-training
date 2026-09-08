# Fil rouge — Assistant de support client e-commerce

Un même cas traverse les six chapitres. Chaque chapitre lui ajoute une brique, de sorte
qu'à la fin de la semaine les participants ont construit un système complet plutôt que six
démonstrations sans lien.

## Le cas

Un détaillant en ligne de taille moyenne reçoit chaque jour plusieurs milliers de
sollicitations client : suivi de commande, conditions de retour, disponibilité produit,
réclamations. Le service client est saturé sur des demandes répétitives, alors que les cas
qui méritent un humain attendent.

L'objectif est un assistant capable de répondre aux demandes courantes, de consulter les
systèmes internes quand la réponse dépend du compte client, et de passer la main à un
conseiller quand il n'est pas en mesure de répondre.

## Pourquoi ce cas

Il a été retenu parce qu'il sollicite réellement les six chapitres, sans qu'aucun ne soit
plaqué artificiellement :

| Chapitre | Ce que le cas exige |
|---|---|
| 0 | Un dépôt de travail et un environnement outillé |
| 1 | Un prompt système qui tienne le ton et le périmètre de la marque |
| 2 | Savoir mesurer si les réponses sont justes avant de les mettre devant un client |
| 3 | Ancrer les réponses dans la base de connaissance : FAQ, conditions de retour, fiches produit |
| 4 | Consulter des systèmes qui ne sont pas des documents : commandes, stock, livraison |
| 5 | Un dialogue multi-tours, une mémoire de conversation, une sortie propre vers un humain |
| 6 | Des données personnelles, plusieurs canaux, et une exposition réelle à l'injection de prompt |

Il a aussi l'avantage de reposer sur des données entièrement synthétiques : aucune
dépendance à un système client, aucun secret à distribuer aux participants.

## Contenu de ce dossier

Le jeu de données est produit avant le chapitre 3, qui en est le premier consommateur
sérieux. Il comprendra :

```
donnees/
  base-connaissance/   FAQ, conditions générales, politique de retour, fiches produit
  commandes/           commandes, expéditions, retours (JSON)
  clients/             comptes clients synthétiques
  conversations/       échanges de support annotés, pour l'évaluation
api/                   API factice exposant commandes, stock et livraison pour le chapitre 4
```

## Progression attendue

| Fin du chapitre | État de l'assistant |
|---|---|
| 1 | Répond à des questions générales, avec un ton et un périmètre maîtrisés |
| 2 | Est mesuré sur un jeu de test, avec une note de départ |
| 3 | Répond en s'appuyant sur la base de connaissance, avec citation des sources |
| 4 | Consulte les commandes et le suivi de livraison via des outils |
| 5 | Tient une conversation, se souvient du contexte, sait passer la main |
| 6 | Est exposé sur deux canaux, journalisé, et résiste aux tentatives d'injection |

## Reste à faire

- [ ] Produire le jeu de données synthétiques
- [ ] Écrire l'API factice du chapitre 4
- [ ] Constituer le jeu de test annoté du chapitre 2
