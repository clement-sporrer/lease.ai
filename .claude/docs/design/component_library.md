# Component library

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Core components

### `AppScreen`

Wrapper avec safe area, background, header optionnel et padding.

Props:

- `title`
- `subtitle`
- `showBack`
- `rightAction`
- `scrollable`

### `PrimaryButton`

CTA principal.

Variants:

- `primary`
- `secondary`
- `outline`
- `danger`
- `disabled`

### `StatusBadge`

Badge de statut métier.

Props:

- `status`
- `label`
- `tone`

### `KpiCard`

Affiche métrique.

Props:

- `label`
- `value`
- `trend`
- `icon`
- `tone`

### `DealCard`

Carte dossier.

Contenu:

- société;
- montant;
- statut;
- dernière mise à jour;
- missing docs count;
- CTA implicite vers détail.

### `LeaseCard`

Carte contrat.

Contenu:

- client;
- statut;
- engagement total;
- prochaine échéance;
- health score.

### `AssetCard`

Carte actif.

Contenu:

- image/icône;
- nom matériel;
- quantité;
- prix unitaire;
- statut;
- contrat lié.

### `PaymentRow`

Ligne échéance.

Contenu:

- date;
- montant;
- statut;
- facture liée;
- icône status.

### `DocumentRow`

Document.

Contenu:

- type;
- nom;
- upload date;
- status validation;
- action view/download.

### `ChecklistItem`

Checklist ADV.

States:

- complete;
- missing;
- warning;
- blocked;
- optional.

### `RiskScoreCard`

Score indicatif ou interne.

Contenu:

- score 0-100;
- band;
- principales raisons;
- flags;
- disclaimer.

### `PricingSummary`

Affiche:

- montant financé;
- durée;
- mensualité;
- marge;
- frais;
- hypothèses.

### `Timeline`

Timeline dossier/contrat.

Props:

- `events`
- `currentStatus`

### `AIInsightCard`

Carte d'insight IA.

Contenu:

- résumé;
- sources utilisées;
- confidence;
- suggested action;
- warning si décision sensible.

## Règles composants

- Tous les composants métier doivent accepter un état `loading` et `error`.
- Les montants doivent passer par un formatter central.
- Les statuts doivent venir de la status machine, pas de strings libres.
- Les composants ne doivent pas décider des permissions: ils reçoivent `canAct` ou les actions filtrées.
