# Compliance checklist

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## MVP compliance checklist

### Auth / accès

- RBAC actif.
- Permissions API.
- Sessions sécurisées.
- Logs actions sensibles.

### Données personnelles

- Minimisation des données.
- Politique de conservation à définir.
- Export/suppression à prévoir.
- Pas de données sensibles dans logs.

### Documents

- Versioning.
- Audit upload/download.
- Signed URLs.
- Chiffrement stockage.

### Signature

- Provider ou mock clairement identifié.
- Preuve de signature en production.
- Contrat signé stocké.

### SEPA

- Mandat requis avant activation.
- IBAN masqué.
- Validation mandat.

### Facturation

- Numérotation facture.
- PDF facture.
- Échéancier.
- Statut paiement.

### Risk

- Score explicable.
- Décision ferme humaine/financeur.
- Overrides justifiés.

### Audit

- Status changes.
- Decisions.
- Document access.
- Activation.
- Payment marking.
