# Unit economics

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Suivre la rentabilité d'un contrat et d'un partenaire.

## Variables

- Montant matériel.
- Durée.
- Loyer mensuel.
- Coût de financement.
- Marge LeaseAI.
- Commission partenaire.
- Coût ADV par dossier.
- Coût intégrations.
- Taux défaut attendu.
- Valeur résiduelle estimée.
- Valeur résiduelle réalisée.

## Unit economics deal

```txt
gross_revenue = monthly_payment * duration_months
funding_cost = financed_amount * refi_rate * duration_factor
partner_commission = financed_amount * commission_rate
ops_cost = adv_minutes * hourly_cost
expected_loss = financed_amount * expected_default_rate * loss_given_default
residual_upside = realized_residual_value - expected_residual_value
contribution_margin = gross_revenue - funding_cost - partner_commission - ops_cost - expected_loss + residual_upside
```

## KPI à afficher CFO

- Contribution margin par deal.
- Marge moyenne par band.
- Coût ADV moyen.
- Commission partenaire.
- Taux de renouvellement.
- Valeur résiduelle réalisée.

## MVP

Les calculs peuvent être simplifiés mais les champs doivent exister pour éviter une refonte plus tard.
