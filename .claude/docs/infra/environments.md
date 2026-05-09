# Environments

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Environnements

### Local

- Développement individuel.
- API locale.
- DB locale ou Docker.
- Feature flags mock actifs.

### Dev

- Intégration continue.
- Données non sensibles.
- Tests rapides.

### Staging

- Pré-production.
- Données seedées réalistes.
- Démo interne.
- Tests E2E.

### Demo

- Stable pour pitch/jury/investors.
- Reset demo.
- Données propres.
- Mocks fiables.

### Production

- Données réelles.
- Pas de reset.
- Monitoring renforcé.
- Intégrations réelles.

## Variables d'environnement

- `API_BASE_URL`
- `APP_ENV`
- `SENTRY_DSN`
- `FEATURE_FLAGS_URL`
- `AUTH_SECRET`
- `DATABASE_URL`
- `OBJECT_STORAGE_BUCKET`
- `LLM_PROVIDER_API_KEY`
- `SIGNATURE_PROVIDER_API_KEY`
