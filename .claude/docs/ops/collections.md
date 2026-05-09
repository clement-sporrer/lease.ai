# Collections

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Gérer les retards de paiement de façon structurée, progressive et traçable.

## MVP

- Détecter échéances en retard.
- Afficher liste admin.
- Créer tâches de relance.
- Marquer régularisation.
- Historiser les actions.

## Statuts retard

- `on_time`
- `late_1_7`
- `late_8_15`
- `late_16_30`
- `late_30_plus`
- `default_risk`
- `regularized`

## Playbook

### J+1

Message simple de rappel.

### J+7

Relance plus formelle, demande régularisation.

### J+15

Escalade ops/finance, plan de régularisation possible.

### J+30

Analyse risque, préparation actions contractuelles.

## UI admin

Afficher:

- client;
- contrat;
- montant dû;
- jours de retard;
- dernière relance;
- prochaine action;
- historique.

## IA

Peut proposer le message de relance et prioriser les cas. Ne doit pas initier d'action juridique seule.
