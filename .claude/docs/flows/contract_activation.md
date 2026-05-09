# Contract activation

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Transformer un accord financeur en contrat actif, sans ambiguïté ni activation prématurée.

## Étapes

```txt
financier_approved
→ firm_offer_generated
→ contract_generated
→ signing
→ signed
→ activation_pending
→ active
```

## Offre ferme

Conditions préalables:

- Accord financeur reçu.
- Pricing final figé.
- Documents minimum présents.
- Client et signataire identifiés.

Contenu:

- Client.
- Matériel.
- Montant.
- Durée.
- Mensualité.
- Conditions clés.
- Validité de l'offre.

## Contrat

Conditions préalables:

- Offre ferme générée.
- Template contrat disponible.
- Données client complètes.
- Données actif/devis complètes.

## Signature

MVP:

- mock signature possible.
- statut signature simulé.
- génération document signé mock.

Production:

- provider e-signature.
- webhook signature.
- preuve de signature.
- archivage probant.

## Activation checklist

Obligatoire:

- Accord financeur reçu.
- Offre ferme générée.
- Contrat signé.
- Mandat SEPA reçu/validé.
- PV livraison reçu.
- Actif créé.
- Échéancier généré.
- Facture fournisseur validée si flux réel.

## Blocages

- Pas de contrat actif sans PV livraison.
- Pas de contrat actif sans mandat SEPA.
- Pas de contrat actif sans actif associé.
- Pas d'activation si contrat non signé.

## Événements

- `offer.generated`
- `contract.generated`
- `signature.started`
- `contract.signed`
- `activation.blocked`
- `contract.activated`
