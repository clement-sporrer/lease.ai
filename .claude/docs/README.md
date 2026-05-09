# README

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif du dossier documentaire

Ce dossier contient les fichiers de cadrage nécessaires avant de lancer le développement de l'application mobile LeaseAI. Il sert de base de travail commune pour les développeurs mobile, backend, product designers, fondateurs business/risk et contributeurs IA.

L'app mobile doit devenir l'interface unifiée de tous les acteurs du cycle de leasing IT:

- **Revendeur / apporteur**: crée et suit les dossiers, dépose devis et pièces, voit les statuts et commissions.
- **PME cliente / locataire**: suit ses contrats, actifs, échéanciers, factures, paiements, documents et renouvellements.
- **ADV / Ops interne**: contrôle les dossiers, déclenche les demandes de pièces, prépare la contractualisation et l'activation.
- **Risk / admin interne**: visualise scoring, pricing, règles, anomalies, package financeur et décision.
- **Financeur / refinanceur**: consulte un package synthétique, décide ou demande clarification.
- **CFO / direction**: suit production, portefeuille, cash, retards, risque et performance.

## Stack recommandée

### Mobile

- React Native avec Expo
- TypeScript strict
- Expo Router pour la navigation
- TanStack Query pour la synchronisation serveur
- Zustand pour les états locaux simples
- React Hook Form + Zod pour les formulaires
- MMKV ou SecureStore pour stockage local léger et sécurisé
- Reanimated pour micro-interactions sobres
- Sentry pour erreurs mobile

### Backend

- FastAPI ou NestJS; ce pack recommande FastAPI pour cohérence avec le guide stratégique.
- PostgreSQL comme source de vérité.
- Stockage objet pour documents, contrats, preuves et exports.
- Jobs async pour génération PDF, notifications, relances et exports.
- API REST v1 documentée dans `/api`.

### Intégrations à acheter plutôt qu'à construire

- Signature électronique
- Archivage probant
- KYC/KYB avancé
- Mandat et prélèvements SEPA
- Email/SMS transactionnels
- Recommandé électronique
- Connecteurs bancaires et comptables

## Ordre de lecture conseillé

1. `00_INDEX.md`
2. `vision/positioning.md`
3. `product/mvp_scope.md`
4. `product/screen_inventory.md`
5. `flows/deal_lifecycle.md`
6. `backend/data_model.md`
7. `api/endpoints.md`
8. `design/design_system.md`
9. `roadmap/development_epics.md`
10. `demo/demo_script.md`

## Principe directeur

Tout ce qui ne réduit pas le temps jusqu'à l'accord, le coût de traitement d'un dossier, la qualité du portefeuille ou la récurrence partenaire n'est pas prioritaire pour le MVP.
