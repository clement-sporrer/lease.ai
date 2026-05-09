# Product principles

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## 1. One clear next action

Chaque écran doit afficher une action principale. Si plusieurs actions sont possibles, l'app doit hiérarchiser:

- action critique;
- action secondaire;
- information.

## 2. Finance-readable

Les données financières ne doivent jamais être noyées dans du texte. Montants, durée, statut de paiement, date d'échéance et exposition doivent être visibles immédiatement.

## 3. Status is a product feature

Un statut n'est pas un label technique. C'est une promesse de clarté. Chaque statut doit avoir:

- nom court;
- explication humaine;
- acteur responsable;
- prochaine étape;
- blockers éventuels.

## 4. No black-box AI

Quand l'IA résume ou recommande, elle doit expliquer sur quels éléments elle s'appuie:

- entreprise;
- documents;
- devis;
- historique;
- règles métier.

## 5. Progressive disclosure

L'app commence légère puis demande davantage d'informations selon le risque. Cette logique est centrale pour créer une expérience rapide sans promettre une absence totale de documents.

## 6. Mobile-first, operator-grade

L'app doit être agréable sur mobile mais ne doit pas ressembler à une app grand public superficielle. Elle doit inspirer contrôle et précision.

## 7. Never hide compliance

Signature, mandat SEPA, PV de livraison, contrat et factures doivent être visibles, versionnés et traçables.

## 8. Build for audit from day one

Toute action sensible crée un audit event:

- decision;
- status change;
- document upload;
- score override;
- pricing override;
- contract activation;
- payment marking.
