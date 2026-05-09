# Acceptance criteria MVP

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Critères globaux

- L'app fonctionne sur iOS et Android en build interne.
- Tous les écrans P0 existent et sont navigables.
- Tous les rôles principaux peuvent se connecter.
- Les permissions sont appliquées côté API.
- Les statuts sont cohérents avec la status machine.
- Aucun écran critique n'a de données incohérentes.

## Deal lifecycle

Accepté si:

- un dossier peut être créé depuis un rôle revendeur;
- un SIREN peut enrichir ou charger un mock stable;
- un devis peut être uploadé;
- une mensualité indicative s'affiche;
- un score s'affiche;
- le dossier peut être soumis;
- l'admin peut le revoir;
- un package financeur peut être généré;
- le financeur peut rendre une décision;
- l'offre ferme et le contrat peuvent être générés;
- la signature peut être simulée;
- le contrat peut être activé seulement si checklist complète.

## Documents

Accepté si:

- upload et download fonctionnent;
- documents obligatoires bloquent activation;
- versions sont conservées;
- types interdits rejetés.

## Dashboards

Accepté si:

- les KPI affichent données réelles de la base;
- les dashboards se mettent à jour après actions;
- les montants sont formatés correctement.

## AI

Accepté si:

- assistant répond sur un deal;
- il explique prochaine action;
- il refuse d'approuver seul;
- réponses sont auditables.
