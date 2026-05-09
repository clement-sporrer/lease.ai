# Contexte pour agent de développement IA

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Résumé très court

LeaseAI est une application mobile et une plateforme backend pour opérer le leasing IT de bout en bout. L'utilisateur ne doit jamais avoir l'impression d'utiliser un simple CRM ou une marketplace: l'expérience doit raconter une société de financement disciplinée, rapide, fiable et pilotée par logiciel.

## Ce qu'il faut construire

Construire une application mobile multi-rôles avec un backend API. Les écrans et permissions changent selon le rôle connecté. Le même objet métier `deal` traverse toute la chaîne: création par un revendeur, enrichissement entreprise, devis, mensualité indicative, score, revue interne, package financeur, accord financeur, offre ferme, contrat, signature, activation, actif loué, échéancier, facture, paiement, dashboard portefeuille.

## Stack cible

Mobile:

- Expo React Native
- TypeScript strict
- Expo Router
- TanStack Query
- Zustand
- React Hook Form + Zod
- Components maison alignés DA LeaseAI

Backend:

- FastAPI
- PostgreSQL
- Object storage
- Async jobs
- REST API v1

## Ne pas faire

- Ne pas construire un scoring ML réel au MVP.
- Ne pas automatiser réellement plusieurs refinanceurs au MVP.
- Ne pas construire un vrai système SEPA complet maison.
- Ne pas laisser l'IA prendre une décision ferme sans review humaine.
- Ne pas créer des écrans vides ou décoratifs: chaque écran doit servir une décision, une preuve, un statut ou une action.

## Priorité de build

1. Auth + rôles.
2. Dashboard par rôle.
3. Création dossier.
4. Enrichissement entreprise via SIREN ou mock stable.
5. Ajout devis et documents.
6. Calcul mensualité indicative.
7. Score indicatif.
8. Soumission et revue interne.
9. Package refinanceur.
10. Accord financeur.
11. Offre ferme.
12. Contrat et signature simulée.
13. Activation.
14. Actif loué.
15. Échéancier, facture, paiement.
16. Dashboard portefeuille.
17. AI assistant contextuel.

## Variables métier clés

- `deal_id`
- `company_id`
- `partner_id`
- `lessee_id`
- `asset_total_value_cents`
- `duration_months`
- `monthly_payment_cents`
- `risk_score`
- `risk_band`
- `deal_status`
- `contract_status`
- `payment_status`
- `missing_documents`

## Style UI

LeaseAI est clair, premium, financier, intelligent, calme. Couleurs principales: Deep Navy, Lease Blue, Teal Green, Soft Blue, White. Typographie: Satoshi pour interface, IBM Plex Mono pour chiffres et données.

## Source of truth

Avant d'implémenter une fonctionnalité, lire:

- screen: `product/screen_specs.md`
- data: `backend/data_model.md`
- status: `backend/status_machine.md`
- API: `api/endpoints.md`
- UI: `design/component_library.md`
- permissions: `product/permissions_matrix.md`
