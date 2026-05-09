# Vue d’ensemble application mobile

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Structure générale

L'app mobile est une expérience multi-rôles. Le rôle détermine les onglets principaux, les actions disponibles, les données visibles et les écrans accessibles.

## Navigation par rôle

### Revendeur

Tabs recommandés:

1. Home
2. Deals
3. New deal
4. Commissions
5. More

### PME cliente

Tabs recommandés:

1. Overview
2. Payments
3. Assets
4. Documents
5. Support

### Admin / ADV

Tabs recommandés:

1. Queue
2. Deals
3. Tasks
4. Portfolio
5. More

### Financeur

Tabs recommandés:

1. Packages
2. Review
3. Decisions
4. Documents
5. Profile

### CFO

Tabs recommandés:

1. Portfolio
2. Cash
3. Risk
4. Partners
5. Reports

## Objets principaux

- Deal
- Company
- Partner
- Quote
- Document
- Risk score
- Pricing proposal
- Refinance package
- Offer
- Contract
- Asset
- Schedule
- Invoice
- Payment
- Task
- Notification
- Audit event

## Écrans à très forte priorité

- Login.
- Dashboard par rôle.
- Deal list.
- Deal detail.
- Create deal.
- Company enrichment.
- Quote upload.
- Indicative offer.
- Missing documents.
- Admin review.
- Refinance package.
- Contract activation.
- Lease overview.
- Payment schedule.
- Asset list.
- Portfolio dashboard.
- AI assistant.

## Patterns d'expérience

### Statut d'abord

Chaque page de dossier doit afficher le statut en haut, avec une phrase simple:

> Accord financeur reçu. Vous pouvez générer l'offre ferme.

### Action suivante claire

Chaque écran métier doit avoir un CTA principal unique.

### Données financières lisibles

Montants, durées et taux doivent être lisibles avec IBM Plex Mono ou équivalent monospace.

### Confiance visuelle

Ne pas surcharger. Utiliser l'espace blanc, les cartes simples, les badges et timelines.
