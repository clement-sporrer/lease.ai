# API errors

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Format erreur

```json
{
  "data": null,
  "meta": {},
  "errors": [
    {
      "code": "DEAL_INVALID_TRANSITION",
      "message": "Transition impossible depuis le statut actuel.",
      "details": {
        "current_status": "submitted",
        "allowed_statuses": ["internal_review"]
      }
    }
  ]
}
```

## Codes principaux

| Code | HTTP | Description |
|---|---:|---|
| `AUTH_INVALID_CREDENTIALS` | 401 | Login invalide |
| `AUTH_TOKEN_EXPIRED` | 401 | Token expiré |
| `PERMISSION_DENIED` | 403 | Permission insuffisante |
| `ENTITY_NOT_FOUND` | 404 | Ressource introuvable |
| `VALIDATION_ERROR` | 422 | Payload invalide |
| `DEAL_INVALID_TRANSITION` | 409 | Transition non autorisée |
| `DEAL_MISSING_REQUIRED_DOCUMENT` | 409 | Document obligatoire manquant |
| `CONTRACT_ACTIVATION_BLOCKED` | 409 | Activation bloquée |
| `PRICING_NOT_AVAILABLE` | 400 | Pricing impossible |
| `RISK_AUTO_REJECT` | 409 | Refus automatique risk |
| `DOCUMENT_TOO_LARGE` | 413 | Fichier trop lourd |
| `DOCUMENT_UNSUPPORTED_TYPE` | 415 | Type fichier interdit |
| `INTEGRATION_UNAVAILABLE` | 503 | Service externe indisponible |

## Règles UI

- Afficher un message humain.
- Afficher la prochaine action si possible.
- Ne jamais afficher directement une stack trace.
- Pour erreurs 403, proposer de changer de rôle si utilisateur multi-rôles.
