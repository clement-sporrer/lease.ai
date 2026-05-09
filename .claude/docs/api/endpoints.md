# API endpoints

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Auth

```txt
POST /auth/login
POST /auth/logout
POST /auth/refresh
POST /auth/forgot-password
GET  /me
POST /me/active-role
```

## Users / organizations

```txt
GET /organizations/current
GET /organizations/{organizationId}
GET /users/{userId}
```

## Deals

```txt
GET    /deals
POST   /deals
GET    /deals/{dealId}
PATCH  /deals/{dealId}
POST   /deals/{dealId}/submit
POST   /deals/{dealId}/status
GET    /deals/{dealId}/timeline
GET    /deals/{dealId}/tasks
```

## Company enrichment

```txt
POST /companies/enrich
GET  /companies/{companyId}
POST /deals/{dealId}/company
```

## Quotes

```txt
POST /deals/{dealId}/quotes
GET  /deals/{dealId}/quotes/{quoteId}
PATCH /deals/{dealId}/quotes/{quoteId}
POST /deals/{dealId}/quotes/{quoteId}/extract
```

## Documents

```txt
GET    /deals/{dealId}/documents
POST   /deals/{dealId}/documents
GET    /documents/{documentId}
GET    /documents/{documentId}/download-url
POST   /documents/{documentId}/validate
POST   /documents/{documentId}/reject
```

## Risk

```txt
POST /deals/{dealId}/risk/assess
GET  /deals/{dealId}/risk/latest
POST /deals/{dealId}/risk/override
```

## Pricing

```txt
POST /pricing/indicative
POST /deals/{dealId}/pricing/recalculate
GET  /deals/{dealId}/pricing
POST /deals/{dealId}/pricing/finalize
```

## ADV / Admin

```txt
GET  /admin/queue
GET  /admin/deals
POST /admin/deals/{dealId}/request-document
POST /admin/deals/{dealId}/pre-approve
POST /admin/deals/{dealId}/reject
GET  /admin/deals/{dealId}/checklist
```

## Refi packages

```txt
POST /deals/{dealId}/refi-package
GET  /refi-packages
GET  /refi-packages/{packageId}
GET  /refi-packages/{packageId}/download-url
POST /refi-packages/{packageId}/send
POST /refi-packages/{packageId}/decision
```

## Offers and contracts

```txt
POST /deals/{dealId}/offers
GET  /offers/{offerId}
POST /offers/{offerId}/send
POST /deals/{dealId}/contracts
GET  /contracts/{contractId}
POST /contracts/{contractId}/send-signature
POST /contracts/{contractId}/mock-sign
GET  /contracts/{contractId}/activation-checklist
POST /contracts/{contractId}/activate
```

## Assets

```txt
GET  /contracts/{contractId}/assets
POST /contracts/{contractId}/assets
GET  /assets/{assetId}
PATCH /assets/{assetId}
```

## Billing / payments

```txt
GET  /contracts/{contractId}/schedule
POST /contracts/{contractId}/schedule/generate
GET  /contracts/{contractId}/invoices
POST /contracts/{contractId}/invoices
GET  /invoices/{invoiceId}
GET  /invoices/{invoiceId}/download-url
POST /invoices/{invoiceId}/mark-sent
POST /invoices/{invoiceId}/mark-paid
GET  /payments
POST /payments
```

## Dashboards

```txt
GET /dashboards/partner
GET /dashboards/client
GET /dashboards/admin
GET /dashboards/cfo/portfolio
GET /dashboards/cfo/cash
GET /dashboards/cfo/risk
```

## AI assistant

```txt
POST /ai/assistant/query
POST /ai/deals/{dealId}/summary
POST /ai/documents/{documentId}/extract
```
