# Data model

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Entités principales

### `users`

- id
- email
- full_name
- phone
- avatar_url
- status
- created_at
- updated_at

### `roles`

- id
- code
- label

### `user_roles`

- user_id
- role_id
- organization_id

### `organizations`

Représente partenaire, client, financeur ou entité interne.

- id
- type: `partner`, `client`, `financier`, `internal`
- legal_name
- trade_name
- siren
- siret
- address
- status

### `companies`

Entreprise locataire enrichie.

- id
- siren
- siret
- legal_name
- address
- activity_code
- creation_date
- legal_status
- active_status
- enrichment_source
- enrichment_payload_json

### `deals`

- id
- public_id
- company_id
- partner_org_id
- client_org_id
- submitted_by_user_id
- status
- amount_cents
- currency
- duration_months
- payment_frequency
- risk_score
- risk_band
- monthly_payment_cents
- created_at
- updated_at

### `quotes`

- id
- deal_id
- supplier_name
- quote_number
- amount_excl_tax_cents
- amount_incl_tax_cents
- currency
- category
- extraction_status
- extraction_payload_json

### `quote_items`

- id
- quote_id
- label
- category
- quantity
- unit_price_cents
- total_price_cents

### `documents`

- id
- deal_id
- contract_id nullable
- organization_id nullable
- type
- status
- file_name
- storage_key
- mime_type
- size_bytes
- version
- uploaded_by_user_id
- validated_by_user_id nullable
- created_at

### `risk_assessments`

- id
- deal_id
- score
- band
- flags_json
- rules_applied_json
- recommendation
- created_by
- version

### `pricing_proposals`

- id
- deal_id
- type: `indicative`, `firm`
- amount_financed_cents
- duration_months
- monthly_payment_cents
- residual_value_cents
- refi_rate
- margin_rate
- fees_cents
- assumptions_json
- version

### `refi_packages`

- id
- deal_id
- status
- financier_org_id
- pdf_document_id
- zip_document_id
- generated_at
- sent_at
- decision_at

### `financier_decisions`

- id
- refi_package_id
- decision: `approved`, `rejected`, `clarification_requested`
- comment
- decided_by_user_id
- decided_at

### `offers`

- id
- deal_id
- status
- pricing_proposal_id
- document_id
- valid_until

### `contracts`

- id
- deal_id
- public_id
- client_org_id
- status
- start_date
- end_date
- signed_at
- activated_at
- total_commitment_cents

### `assets`

- id
- contract_id
- name
- category
- serial_number nullable
- quantity
- unit_value_cents
- residual_value_cents
- status

### `payment_schedules`

- id
- contract_id
- due_date
- amount_cents
- status
- invoice_id nullable
- payment_id nullable

### `invoices`

- id
- contract_id
- invoice_number
- issue_date
- due_date
- amount_cents
- vat_cents
- status
- pdf_document_id

### `payments`

- id
- contract_id
- invoice_id
- amount_cents
- received_at
- method
- status
- reference

### `tasks`

- id
- assignee_user_id
- deal_id nullable
- contract_id nullable
- type
- status
- due_at
- title
- description

### `audit_events`

- id
- actor_user_id
- entity_type
- entity_id
- event_type
- payload_json
- created_at

## Relations clés

- Un partner crée plusieurs deals.
- Un deal appartient à une company.
- Un deal a un quote principal, plusieurs documents, plusieurs risk assessments.
- Un deal peut générer un refi package, une offre, un contrat.
- Un contrat a plusieurs assets, schedules, invoices, payments.
