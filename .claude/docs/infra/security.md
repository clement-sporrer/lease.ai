# Infrastructure security

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Secrets

- Aucun secret dans le repo.
- Secrets via gestionnaire sécurisé.
- Rotation périodique.

## Réseau

- API HTTPS uniquement.
- CORS strict.
- Rate limiting auth.

## Base de données

- Backups automatiques.
- Chiffrement at rest.
- Accès restreint.
- Logs d'accès admin.

## Object storage

- Buckets privés.
- Signed URLs courtes.
- Chiffrement.
- Audit downloads.

## Mobile

- Pas de secrets durables dans l'app.
- SecureStore pour tokens.
- Logout efface tokens.
- Protection basique contre sessions expirées.

## Admin

- MFA recommandé.
- Permissions minimales.
- Audit renforcé.
