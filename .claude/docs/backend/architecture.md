# Architecture technique

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Vue d'ensemble

```txt
Mobile App (Expo/React Native)
        ↓ REST API
Backend API (FastAPI)
        ↓
PostgreSQL + Object Storage
        ↓
Async Jobs / PDF / Notifications / Integrations
        ↓
BI + Analytics + Audit Logs
```

## Couches

### 1. Mobile app

- UI multi-rôles.
- Navigation conditionnelle.
- Formulaires.
- Uploads.
- Dashboard.
- Assistant IA.

### 2. API backend

- Auth.
- RBAC.
- Deals.
- Documents.
- Scoring.
- Pricing.
- Contracts.
- Assets.
- Billing.
- Payments.
- Reporting.

### 3. Domain services

- DealService.
- CompanyEnrichmentService.
- PricingService.
- RiskService.
- DocumentService.
- RefiPackageService.
- ContractService.
- BillingService.
- PaymentService.
- AuditService.
- NotificationService.

### 4. Persistence

- PostgreSQL pour données métier.
- Object storage pour documents.
- Audit logs append-only.

### 5. Async jobs

- Génération PDF.
- Extraction documents.
- Envoi notification.
- Génération facture.
- Relance.
- Analytics refresh.

## Environnements

- `local`
- `dev`
- `staging`
- `demo`
- `prod`

## Principes

- API first.
- Mobile ne contient pas de logique de décision critique.
- Statuts validés backend.
- Toute action sensible auditée.
- Mocks contrôlés par feature flags.
