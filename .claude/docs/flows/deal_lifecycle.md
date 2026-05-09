# Deal lifecycle

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Vue globale

```txt
lead
→ draft
→ company_enriched
→ quote_added
→ indicative_offer_ready
→ submitted
→ internal_review
→ missing_documents
→ pre_approved
→ refi_package_ready
→ refi_review
→ financier_approved
→ firm_offer_generated
→ contract_generated
→ signing
→ signed
→ activation_pending
→ active
→ in_repayment
→ renewal_window
→ closed
```

## Statuts principaux

### `draft`

Dossier créé mais incomplet. Peut être supprimé ou modifié par le revendeur.

### `company_enriched`

Entreprise identifiée et enrichie. Le revendeur doit confirmer ou corriger.

### `quote_added`

Devis ajouté. Le système peut calculer montant, catégorie et mensualité.

### `indicative_offer_ready`

Mensualité indicative et score affichables. Le dossier n'est pas encore soumis.

### `submitted`

Le revendeur a soumis le dossier. Modification limitée.

### `internal_review`

ADV/risk vérifie dossier, documents, score, pricing et cohérence.

### `missing_documents`

Des pièces bloquent la suite. Le dossier revient côté revendeur/client selon le document.

### `pre_approved`

Pré-accord interne. Le dossier peut être packagé pour financeur.

### `refi_package_ready`

Package créé mais pas encore envoyé/assigné.

### `refi_review`

Financeur consulte le dossier.

### `financier_approved`

Accord financeur reçu. Offre ferme possible.

### `firm_offer_generated`

Offre ferme générée.

### `contract_generated`

Contrat créé, en attente d'envoi signature.

### `signing`

Signature en cours.

### `signed`

Contrat signé, mais pas encore actif.

### `activation_pending`

Attente mandat SEPA, PV livraison ou création actif/échéancier.

### `active`

Contrat actif. Facturation et paiements peuvent démarrer.

### `in_repayment`

Contrat vivant avec échéances en cours.

### `renewal_window`

Fenêtre de renouvellement ouverte.

### `closed`

Contrat terminé.

## Transitions interdites

- `draft` -> `firm_offer_generated`
- `submitted` -> `active`
- `refi_review` -> `contract_generated` sans `financier_approved`
- `signed` -> `active` sans activation checklist complète
- `active` -> `draft`

## Actions sensibles à auditer

- Soumission dossier.
- Demande pièce.
- Pré-accord.
- Refus.
- Génération package.
- Décision financeur.
- Génération offre ferme.
- Signature.
- Activation.
- Marquage paiement.
