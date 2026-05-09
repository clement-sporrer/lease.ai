# Pricing logic MVP

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Calculer une mensualité indicative rapidement et de façon explicable. La logique MVP peut être simplifiée, mais doit être cohérente et paramétrable.

## Inputs

- Montant matériel HT/TTC.
- Durée souhaitée: 24, 36, 48 ou 60 mois.
- Fréquence: mensuelle par défaut.
- Catégorie matériel.
- Score band.
- Marge LeaseAI cible.
- Coût de financement/refi estimé.
- Frais éventuels.
- Valeur résiduelle estimée simple.

## Formule indicative simple

```txt
base_financed_amount = quote_amount + setup_fees
risk_margin = margin_by_score_band[band]
refi_cost = refi_rate_by_duration[duration]
residual_value = quote_amount * residual_value_rate[category][duration]
amount_to_amortize = base_financed_amount - residual_value
monthly_payment = amortized_payment(amount_to_amortize, refi_cost + risk_margin, duration)
```

## Paramètres MVP

### Durées

| Durée | Coût refi indicatif |
|---:|---:|
| 24 mois | 4.5% |
| 36 mois | 5.0% |
| 48 mois | 5.5% |
| 60 mois | 6.0% |

### Marge par band

| Band | Marge |
|---|---:|
| A | 2.0% |
| B | 2.8% |
| C | 4.0% |
| D | 6.0% |
| E | N/A |

### Valeur résiduelle simplifiée

| Catégorie | 24m | 36m | 48m | 60m |
|---|---:|---:|---:|---:|
| Laptops | 25% | 15% | 8% | 3% |
| Phones | 30% | 18% | 10% | 4% |
| Monitors | 20% | 12% | 6% | 2% |
| Network | 18% | 10% | 5% | 2% |
| Other | 10% | 5% | 0% | 0% |

## Disclaimers UI

Toujours afficher:

> Mensualité indicative, sous réserve de validation du dossier, du financeur et des documents contractuels.

## Backend

Les paramètres doivent être stockés en table ou config versionnée. Toute modification de paramètres doit être auditée.

## API

- `POST /pricing/indicative`
- `POST /deals/{dealId}/pricing/recalculate`
- `GET /deals/{dealId}/pricing`
