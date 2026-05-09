# Renewal and remarketing

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Préparer la boucle de valeur long terme: renouvellement, prolongation, restitution, reconditionnement, revente ou relocation.

## MVP light

Le MVP doit seulement afficher une fenêtre de renouvellement et permettre de créer une intention.

## Statuts fin de contrat

- `not_due`;
- `renewal_window`;
- `renewal_offer_created`;
- `renewed`;
- `extension_requested`;
- `return_requested`;
- `returned`;
- `remarketed`;
- `closed`.

## Déclencheur

À J-90 avant fin de contrat:

- créer notification client;
- créer tâche partenaire/ops;
- afficher options.

## Options client

- Renouveler avec nouveau matériel.
- Prolonger le contrat.
- Restituer le matériel.
- Demander rappel.

## Données utiles

- Type d'actif.
- Date fin contrat.
- Valeur résiduelle prévue.
- Paiements à jour.
- Satisfaction client.
- Performance revendeur.

## IA possible

L'assistant peut suggérer:

- client prioritaire à contacter;
- actifs à renouveler;
- option économiquement favorable;
- risque de non-renouvellement.

Mais la décision commerciale reste humaine.
