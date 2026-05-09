# File storage

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Stocker et servir les documents de façon sécurisée, traçable et compatible avec un futur archivage probant.

## Buckets recommandés

- `leaseai-documents-dev`
- `leaseai-documents-staging`
- `leaseai-documents-prod`

## Chemins

```txt
/orgs/{organizationId}/deals/{dealId}/{documentType}/v{version}/{fileName}
/contracts/{contractId}/{documentType}/v{version}/{fileName}
/invoices/{invoiceId}/{fileName}
/refi-packages/{packageId}/{fileName}
```

## Metadata document

Toujours stocker en base:

- storage_key;
- original_file_name;
- normalized_file_name;
- mime_type;
- size_bytes;
- checksum;
- uploaded_by;
- uploaded_at;
- version;
- document_type;
- status.

## Sécurité

- Pas d'URL publique permanente.
- Signed URLs temporaires.
- Vérification permission avant génération URL.
- Chiffrement at rest.
- Limite de taille fichier.
- Types MIME autorisés.

## Types autorisés MVP

- PDF.
- PNG/JPEG.
- DOCX optionnel pour contrats modèles.

## Versioning

Un document remplacé ne doit pas effacer l'ancien. Créer une nouvelle version.

## Audit

À tracer:

- upload;
- view/download;
- validation;
- rejet;
- suppression logique;
- génération PDF.
