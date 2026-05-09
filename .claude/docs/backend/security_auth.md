# Security and auth

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Authentification

MVP:

- Email/password.
- JWT access token court.
- Refresh token sécurisé.
- Logout.
- Reset password simple.

Production:

- MFA pour admin/risk/financeur.
- SSO entreprise optionnel.
- Device/session management.

## RBAC

Chaque endpoint doit vérifier:

1. utilisateur authentifié;
2. rôle actif;
3. organisation associée;
4. permission sur l'entité;
5. action autorisée selon statut.

## Scoping des données

### Partner

Ne voit que ses deals.

### Client

Ne voit que ses contrats/documents/factures.

### Financier

Ne voit que les packages assignés.

### Ops/Risk/Admin

Voit selon permission interne.

### CFO

Voit données agrégées et lecture étendue.

## Données sensibles

- Documents d'identité.
- RIB/IBAN.
- Contrats.
- Mandats SEPA.
- Décisions risk.
- Logs d'audit.

## Règles

- Ne jamais logger de secrets.
- Ne jamais stocker mot de passe en clair.
- Ne jamais exposer `storage_key` direct dans l'app si non nécessaire.
- Masquer partiellement IBAN dans UI.
- Justification obligatoire pour overrides risk/pricing.

## Audit obligatoire

- Login admin.
- View/download document sensible.
- Status change.
- Decision.
- Override.
- Activation.
- Payment marking.
