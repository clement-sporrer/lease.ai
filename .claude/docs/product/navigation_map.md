# Navigation map

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Structure Expo Router proposée

```txt
app/
  (auth)/
    login.tsx
    forgot-password.tsx
  (role-switch)/
    index.tsx
  (partner)/
    _layout.tsx
    home.tsx
    deals/
      index.tsx
      [dealId].tsx
      create.tsx
      [dealId]/company.tsx
      [dealId]/quote.tsx
      [dealId]/offer.tsx
      [dealId]/documents.tsx
    commissions.tsx
    more.tsx
  (client)/
    _layout.tsx
    overview.tsx
    leases/[leaseId].tsx
    payments.tsx
    assets.tsx
    documents.tsx
    support.tsx
  (admin)/
    _layout.tsx
    queue.tsx
    deals/[dealId].tsx
    review/[dealId].tsx
    package/[dealId].tsx
    activation/[contractId].tsx
    portfolio.tsx
  (financier)/
    _layout.tsx
    packages.tsx
    packages/[packageId].tsx
    decision/[packageId].tsx
  (cfo)/
    _layout.tsx
    portfolio.tsx
    cash.tsx
    risk.tsx
    partners.tsx
  shared/
    ai-assistant.tsx
    notifications.tsx
    profile.tsx
    document-viewer.tsx
```

## Règles de navigation

- Après login, appeler `GET /me`.
- Si un seul rôle: redirection directe vers le layout du rôle.
- Si plusieurs rôles: afficher `Role switcher`.
- Les deep links doivent vérifier la permission côté API.
- Aucun écran admin ne doit être accessible par simple manipulation d'URL.

## Navigation Partner

```txt
Home -> Deals -> Deal detail
Home -> New deal -> Company -> Quote -> Offer -> Score -> Missing docs -> Submit
Deal detail -> Documents
Deal detail -> Timeline
Deal detail -> AI Assistant contextualized
```

## Navigation Client

```txt
Overview -> Lease detail
Overview -> Next payment -> Payment detail
Assets -> Asset detail
Documents -> Document viewer
Support -> Ticket/chat light
```

## Navigation Admin

```txt
Queue -> Deal review -> Checklist -> Request document
Deal review -> Generate refi package -> Package preview
Deal review -> Firm offer -> Contract generation -> Signature tracking -> Activation checklist
Portfolio -> Deal/contract detail
```

## Navigation Financier

```txt
Packages -> Package detail -> Risk/pricing -> Documents -> Decision
```
