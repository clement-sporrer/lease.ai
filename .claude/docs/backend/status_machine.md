# Status machine

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Deal statuses

```ts
export type DealStatus =
  | 'draft'
  | 'company_enriched'
  | 'quote_added'
  | 'indicative_offer_ready'
  | 'submitted'
  | 'internal_review'
  | 'missing_documents'
  | 'pre_approved'
  | 'refi_package_ready'
  | 'refi_review'
  | 'financier_approved'
  | 'financier_rejected'
  | 'firm_offer_generated'
  | 'contract_generated'
  | 'signing'
  | 'signed'
  | 'activation_pending'
  | 'active'
  | 'cancelled';
```

## Contract statuses

```ts
export type ContractStatus =
  | 'draft'
  | 'generated'
  | 'sent_for_signature'
  | 'signed'
  | 'activation_pending'
  | 'active'
  | 'in_repayment'
  | 'renewal_window'
  | 'closed'
  | 'defaulted'
  | 'cancelled';
```

## Document statuses

```ts
export type DocumentStatus =
  | 'required'
  | 'uploaded'
  | 'extracting'
  | 'validated'
  | 'rejected'
  | 'missing'
  | 'expired';
```

## Allowed transitions example

```ts
export const allowedDealTransitions = {
  draft: ['company_enriched', 'cancelled'],
  company_enriched: ['quote_added', 'cancelled'],
  quote_added: ['indicative_offer_ready', 'cancelled'],
  indicative_offer_ready: ['submitted', 'cancelled'],
  submitted: ['internal_review'],
  internal_review: ['missing_documents', 'pre_approved', 'financier_rejected'],
  missing_documents: ['internal_review', 'cancelled'],
  pre_approved: ['refi_package_ready'],
  refi_package_ready: ['refi_review'],
  refi_review: ['financier_approved', 'financier_rejected', 'missing_documents'],
  financier_approved: ['firm_offer_generated'],
  firm_offer_generated: ['contract_generated'],
  contract_generated: ['signing'],
  signing: ['signed'],
  signed: ['activation_pending'],
  activation_pending: ['active'],
  active: [],
};
```

## Validation backend

Le backend doit refuser toute transition non autorisée avec:

- code erreur;
- statut actuel;
- statuts possibles;
- raison du blocage.

## UI mapping

Chaque statut doit exposer:

- label;
- couleur;
- description;
- next_action;
- responsible_role.
