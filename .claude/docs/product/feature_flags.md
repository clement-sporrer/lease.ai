# Feature flags

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Les feature flags permettent de livrer vite, de simuler certaines intégrations, et de séparer démo, bêta et production.

## Flags recommandés

| Flag | Type | Description | Défaut MVP |
|---|---|---|---|
| `mock_company_enrichment` | backend | Utilise données mock si API indisponible | true |
| `mock_signature` | backend | Simule signature électronique | true |
| `mock_sepa` | backend | Simule mandat SEPA | true |
| `mock_payment_received` | backend | Permet marquage manuel paiement | true |
| `enable_financier_portal` | frontend/backend | Active espace financeur | true |
| `enable_ai_assistant` | frontend/backend | Active assistant contextuel | true |
| `enable_commissions` | frontend/backend | Commissions partenaire | partial |
| `enable_renewal` | frontend/backend | Renouvellement | partial |
| `enable_lre_collections` | backend | Recommandé électronique | false |
| `enable_real_bank_sync` | backend | Sync bancaire réelle | false |
| `enable_advanced_risk_override` | backend | Override risk détaillé | false |

## Niveaux d'environnement

### Demo

- Beaucoup de mocks.
- Données seedées.
- Bouton reset demo.

### Beta

- Mocks réduits.
- Upload réel.
- Signature éventuellement réelle.
- Paiements encore semi-manuels.

### Production

- Audit strict.
- Pas de reset.
- Permissions renforcées.
- Intégrations critiques réelles.
