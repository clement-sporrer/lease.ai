# Deployment

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Mobile

### Branches

- `main`: stable.
- `develop`: intégration.
- `feature/*`: features.

### Builds

- Expo EAS build.
- Internal distribution pour test.
- TestFlight / Play Console selon cible.

### Release process

1. Merge feature.
2. Tests unitaires.
3. Tests E2E critiques.
4. Build staging.
5. QA.
6. Build production.
7. Release notes.

## Backend

- CI lint/test.
- Migration DB.
- Deploy staging.
- Smoke tests.
- Deploy production.

## Migrations

- Versionnées.
- Testées en staging.
- Pas de migration destructive sans backup.

## Rollback

- Conserver version précédente backend.
- Feature flags pour désactiver features instables.
- Mobile: hotfix via OTA si possible.
