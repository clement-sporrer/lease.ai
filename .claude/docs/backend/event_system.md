# Event system

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Les événements métier permettent l'audit, les notifications, les analytics et les jobs async.

## Naming

Format:

```txt
entity.action
```

Exemples:

- `deal.created`
- `deal.submitted`
- `document.uploaded`
- `risk.assessed`
- `pricing.calculated`
- `refi_package.generated`
- `financier.approved`
- `offer.generated`
- `contract.signed`
- `contract.activated`
- `invoice.generated`
- `payment.received`

## Event payload standard

```json
{
  "event_id": "evt_...",
  "event_type": "deal.submitted",
  "actor_user_id": "usr_...",
  "entity_type": "deal",
  "entity_id": "deal_...",
  "occurred_at": "2026-04-26T12:00:00Z",
  "payload": {},
  "request_id": "req_..."
}
```

## Events MVP

### Deal

- `deal.created`
- `deal.company_enriched`
- `deal.quote_added`
- `deal.indicative_offer_ready`
- `deal.submitted`
- `deal.status_changed`
- `deal.cancelled`

### Document

- `document.upload_started`
- `document.uploaded`
- `document.extraction_started`
- `document.extraction_failed`
- `document.validated`
- `document.rejected`

### Risk/Pricing

- `risk.assessed`
- `risk.override_requested`
- `risk.override_applied`
- `pricing.calculated`
- `pricing.finalized`

### Refi

- `refi_package.generated`
- `refi_package.sent`
- `financier.decision_submitted`

### Contract/Billing

- `offer.generated`
- `contract.generated`
- `signature.started`
- `contract.signed`
- `contract.activated`
- `schedule.generated`
- `invoice.generated`
- `payment.received`

## Notifications dérivées

- Quand `deal.missing_documents`: notifier partenaire.
- Quand `financier.decision_submitted`: notifier admin et partenaire.
- Quand `contract.signed`: notifier admin.
- Quand `invoice.generated`: notifier client.
- Quand `payment.late`: notifier ops.
