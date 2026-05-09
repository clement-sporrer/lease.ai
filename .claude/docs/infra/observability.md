# Observability

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Détecter rapidement erreurs produit, API, jobs et intégrations.

## Logs

- request_id.
- user_id si disponible.
- role.
- entity_id.
- event_type.
- status_code.
- duration_ms.

## Metrics API

- Latence p50/p95.
- Taux erreur.
- Auth failures.
- Upload failures.
- PDF generation failures.
- Jobs queue length.

## Metrics produit

- Deals created.
- Deals submitted.
- Transitions par statut.
- Documents uploaded.
- Contracts activated.
- Payments marked received.

## Alerts MVP

- API down.
- Login failure spike.
- Upload failure spike.
- Contract activation failures.
- PDF generation failures.

## Sentry mobile

Capturer:

- crash;
- navigation errors;
- network errors;
- unhandled promise rejection;
- app version.
