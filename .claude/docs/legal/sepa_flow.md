# SEPA flow

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Collecter et valider les informations nécessaires au prélèvement récurrent.

## MVP

- Upload RIB.
- Upload ou génération mandat SEPA mock.
- Validation manuelle admin.
- Masquage IBAN dans UI.

## Production

- Créancier avec ICS.
- Mandat SEPA signé.
- Stockage sécurisé.
- Transmission PSP/banking.
- Gestion rejets.

## Données mandat

- Référence unique de mandat.
- Nom débiteur.
- Adresse débiteur.
- IBAN.
- BIC optionnel.
- Nom créancier.
- ICS.
- Type de paiement: récurrent.
- Date signature.

## Statuts mandat

- `missing`;
- `uploaded`;
- `pending_validation`;
- `validated`;
- `rejected`;
- `revoked`.

## UI activation

Le mandat SEPA est un blocker d'activation. Tant que le mandat n'est pas validé, le CTA `Activer contrat` reste disabled.
