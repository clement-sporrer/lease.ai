# OpenAPI conventions

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Base URL

```txt
/api/v1
```

## Auth

Header:

```txt
Authorization: Bearer <access_token>
```

## Format réponse standard

```json
{
  "data": {},
  "meta": {},
  "errors": []
}
```

## Pagination

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 133
  }
}
```

## Dates

- ISO 8601 UTC côté API.
- Format local côté UI.

## Montants

Toujours en centimes:

```json
{
  "amount_cents": 8545000,
  "currency": "EUR"
}
```

## Ids

- `id`: UUID interne.
- `public_id`: ID lisible, ex `D-2026-0001`.

## Erreurs

Voir `api/errors.md`.

## Versioning

- `/api/v1` pour MVP.
- Ne pas casser contrats API sans version.
