# Payment and billing flow

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Gérer échéanciers, factures, paiements et visibilité cash.

## Échéancier

Créé à l'activation du contrat.

Champs:

- contract_id;
- due_date;
- amount_cents;
- currency;
- status;
- invoice_id;
- payment_id.

Statuts échéance:

- `upcoming`;
- `invoiced`;
- `paid`;
- `late`;
- `failed`;
- `cancelled`.

## Facture

Générée selon échéancier ou manuellement en MVP.

Champs:

- invoice_number;
- invoice_date;
- due_date;
- amount;
- VAT;
- PDF URL;
- status.

Statuts facture:

- `draft`;
- `issued`;
- `sent`;
- `paid`;
- `overdue`;
- `void`.

## Paiement

MVP:

- Paiement marqué reçu manuellement par admin.
- Rejet simulé possible.

Production:

- Webhooks PSP/banking/SEPA.
- Réconciliation.
- Relances automatiques.

Statuts paiement:

- `pending`;
- `received`;
- `failed`;
- `refunded`;
- `reconciled`.

## UI client

Afficher:

- prochaine échéance;
- échéancier complet;
- factures téléchargeables;
- paiements reçus;
- retards éventuels.

## UI admin/CFO

Afficher:

- cash attendu;
- cash collecté;
- retards;
- taux de rejet;
- échéances à venir;
- clients en retard.

## Événements

- `schedule.generated`
- `invoice.generated`
- `invoice.sent`
- `payment.received`
- `payment.failed`
- `payment.reconciled`
- `payment.late`
