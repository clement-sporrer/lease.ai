# Risk rules MVP

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Le scoring MVP doit être un moteur de règles explicable, pas un modèle ML. Il doit produire un score indicatif, des flags et une recommandation de traitement.

## Score

Échelle: 0 à 100.

Bands:

| Band | Score | Signification |
|---|---:|---|
| A | 80-100 | Favorable |
| B | 65-79 | Acceptable avec revue standard |
| C | 50-64 | Revue renforcée |
| D | 30-49 | Risque élevé |
| E | 0-29 | Refus probable |

## Inputs initiaux

- Ancienneté entreprise.
- Statut actif.
- Cohérence SIREN.
- Montant devis.
- Catégorie matériel.
- Durée.
- Ratio montant/ancienneté approximatif.
- Historique LeaseAI si existant.
- Qualité partenaire.
- Documents présents.

## Règles positives

- Entreprise active: +15.
- Ancienneté > 3 ans: +15.
- Montant < 25k€: +10.
- Matériel IT standard: +10.
- Revendeur fiable: +10.
- Documents minimum présents: +10.
- Aucun flag majeur: +10.

## Règles négatives

- Entreprise inactive/radiée: refus automatique.
- SIREN introuvable: blocage.
- Devis incohérent ou illisible: -20.
- Entreprise < 12 mois: -15.
- Montant > 50k€: revue renforcée.
- Catégorie matériel non standard: -10.
- Signataire non identifié: blocker avant contrat.
- RIB manquant: blocker avant activation.

## Flags

- `company_too_young`
- `company_inactive`
- `large_ticket`
- `non_standard_asset`
- `missing_quote`
- `missing_signer_identity`
- `missing_bank_details`
- `partner_low_quality`
- `pricing_outside_policy`

## Recommandations système

| Situation | Recommandation |
|---|---|
| Band A/B et documents présents | Pré-accord interne possible |
| Band C | Revue risk |
| Band D | Revue senior ou refus |
| Band E | Refus probable |
| Refus auto | Bloquer et expliquer |

## UI

Le revendeur voit un résumé simplifié: favorable, à compléter, revue nécessaire. L'admin/risk voit score complet, flags, règles appliquées et justification.
