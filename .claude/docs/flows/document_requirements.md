# Document requirements

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Types de documents

| Code | Document | Obligatoire MVP | Source |
|---|---|---:|---|
| `quote` | Devis fournisseur | Oui | Revendeur |
| `company_extract` | Extrait entreprise | Auto/mock | Système |
| `identity_signer` | Identité signataire | Selon cas | Client |
| `bank_details` | RIB/IBAN | Oui avant activation | Client |
| `sepa_mandate` | Mandat SEPA | Oui avant activation | Client/Ops |
| `signed_offer` | Offre signée | Selon flow | Système |
| `contract` | Contrat | Oui | Système |
| `signed_contract` | Contrat signé | Oui | Signature provider |
| `delivery_certificate` | PV livraison | Oui avant activation | Revendeur/Client |
| `invoice_supplier` | Facture fournisseur | Oui pour déblocage réel | Revendeur/Ops |
| `refi_package` | Package financeur | Oui pour refi | Système |
| `customer_invoice` | Facture loyer | Oui contrat actif | Système |

## Logique progressive

### Au démarrage

- SIREN.
- Devis.
- Contact client.

### Avant soumission

- Devis complet.
- Montant extrait.
- Catégorie matériel.
- Durée souhaitée.

### Avant package financeur

- Devis validé.
- Données entreprise.
- Résumé scoring.
- Documents critiques selon montant.

### Avant offre ferme

- Accord financeur.
- Pricing final.
- Conditions.

### Avant activation

- Contrat signé.
- Mandat SEPA.
- PV livraison.
- Actif créé.
- Échéancier.

## Règles par montant MVP

| Montant matériel | Documents minimum |
|---:|---|
| < 10k€ | SIREN + devis + contact + IBAN avant activation |
| 10k€ - 50k€ | + identité signataire + RIB + PV livraison |
| > 50k€ | + revue risk renforcée + éventuelles pièces financières |

## États document

- `required`
- `uploaded`
- `extracting`
- `validated`
- `rejected`
- `expired`
- `missing`

## Règle de nommage

```txt
{dealId}_{documentType}_{version}_{yyyyMMdd}.{ext}
```

Exemple:

```txt
D-2026-0001_quote_v1_20260426.pdf
```
