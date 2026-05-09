# Tracking plan

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Mesurer usage produit, conversion, efficacité ops et qualité portefeuille.

## Events mobile

| Event | Properties |
|---|---|
| `app_opened` | role, version |
| `login_succeeded` | role |
| `deal_create_started` | partner_id |
| `company_enrichment_requested` | deal_id |
| `company_enrichment_completed` | deal_id, source, duration_ms |
| `quote_uploaded` | deal_id, file_type, size |
| `quote_extracted` | deal_id, success, confidence |
| `indicative_offer_viewed` | deal_id, amount, duration |
| `deal_submitted` | deal_id, missing_docs_count |
| `document_uploaded` | deal_id, type |
| `admin_review_opened` | deal_id |
| `refi_package_generated` | deal_id |
| `financier_decision_submitted` | package_id, decision |
| `contract_sent_for_signature` | contract_id |
| `contract_signed` | contract_id |
| `contract_activated` | contract_id |
| `invoice_viewed` | invoice_id |
| `payment_marked_received` | payment_id |
| `ai_assistant_opened` | role, context_type |
| `ai_assistant_question_asked` | role, context_type |

## Properties standard

- user_id.
- role.
- organization_id.
- app_version.
- environment.
- entity_id.

## Funnels

### Deal creation funnel

Create started -> company enriched -> quote uploaded -> offer viewed -> submitted.

### Contract funnel

Submitted -> internal review -> pre-approved -> refi approved -> offer -> signed -> active.

### Payment funnel

Schedule generated -> invoice issued -> payment received -> reconciled.

## Privacy

Ne pas tracker de données sensibles brutes. Utiliser IDs et catégories.
