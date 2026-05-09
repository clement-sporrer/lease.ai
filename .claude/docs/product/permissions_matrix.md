# Permissions matrix

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Rôles

- `partner_user`
- `client_user`
- `ops_user`
- `risk_user`
- `admin_user`
- `financier_user`
- `cfo_user`

## Matrice synthétique

| Action | Partner | Client | Ops | Risk | Admin | Financier | CFO |
|---|---:|---:|---:|---:|---:|---:|---:|
| Créer dossier | Oui | Non | Oui | Oui | Oui | Non | Non |
| Voir ses dossiers | Oui | Non | Oui | Oui | Oui | Assignés | Lecture |
| Voir tous dossiers | Non | Non | Oui | Oui | Oui | Non | Oui |
| Upload devis | Oui | Non | Oui | Oui | Oui | Non | Non |
| Upload pièce | Oui | Oui | Oui | Oui | Oui | Non | Non |
| Voir score | Résumé | Non | Oui | Oui | Oui | Oui | Agrégé |
| Modifier score | Non | Non | Non | Override | Oui | Non | Non |
| Voir pricing | Indicatif | Contrat | Oui | Oui | Oui | Oui | Agrégé |
| Modifier pricing | Non | Non | Non | Override | Oui | Non | Non |
| Demander pièce | Non | Non | Oui | Oui | Oui | Clarification | Non |
| Pré-accorder | Non | Non | Oui | Oui | Oui | Non | Non |
| Générer package | Non | Non | Oui | Oui | Oui | Non | Non |
| Décider refi | Non | Non | Non | Non | Non | Oui | Non |
| Générer offre ferme | Non | Non | Oui | Oui | Oui | Non | Non |
| Signer contrat | Non | Oui si signataire | Non | Non | Non | Non | Non |
| Activer contrat | Non | Non | Oui | Oui | Oui | Non | Non |
| Voir factures | Non | Oui | Oui | Oui | Oui | Non | Oui |
| Marquer paiement reçu | Non | Non | Oui | Non | Oui | Non | Non |
| Export reporting | Non | Non | Non | Oui | Oui | Non | Oui |

## Règle fondamentale

Le frontend cache les actions non autorisées, mais l'API doit toujours valider les permissions. Le frontend n'est jamais une barrière de sécurité suffisante.
