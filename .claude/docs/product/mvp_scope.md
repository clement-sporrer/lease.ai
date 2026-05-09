# Périmètre MVP mobile

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Définition du MVP

Le MVP mobile complet doit permettre de démontrer et d'utiliser le cycle LeaseAI de bout en bout pour les principaux rôles. Il ne s'agit pas seulement d'une app de consultation: elle doit gérer la création, le suivi, la décision, la contractualisation et la vie active d'un contrat.

## Inclus dans le MVP

### Authentification et rôles

- Login email/password.
- SSO mock optionnel.
- Sélection de rôle si utilisateur multi-rôles.
- Session sécurisée.
- RBAC côté API et côté UI.

### Revendeur

- Dashboard revendeur.
- Création dossier.
- Saisie SIREN.
- Enrichissement entreprise.
- Ajout devis IT.
- Upload documents.
- Mensualité indicative.
- Score indicatif.
- Pièces manquantes.
- Soumission dossier.
- Suivi statut.
- Commissions indicatives.

### PME cliente

- Dashboard contrats.
- Vue contrat actif.
- Actifs loués.
- Échéancier.
- Factures.
- Paiements.
- Documents.
- Support.
- Renouvellement simple.

### Admin / ADV

- Liste dossiers.
- Revue dossier.
- Checklist ADV.
- Demande pièce.
- Pré-accord.
- Package financeur.
- Statut financeur.
- Offre ferme.
- Contrat.
- Signature simulée/intégrée.
- Mandat SEPA.
- PV livraison.
- Activation.

### Financeur

- Liste packages assignés.
- Résumé risque.
- Résumé pricing.
- Documents.
- Décision: accord, refus, clarification.

### Direction / CFO

- Dashboard portefeuille.
- Production.
- Cash collecté.
- Paiements en retard.
- Exposition.
- Performance partenaires.

### AI assistant

- Assistant contextuel.
- Explication statut.
- Résumé dossier.
- Questions simples sur un deal.
- Recommandation de prochaine action.

## Exclu du MVP

- Vrai scoring ML entraîné.
- Multi-pays.
- Multi-refinanceurs automatisés sophistiqués.
- Marketplace fournisseurs.
- Moteur avancé de valeur résiduelle.
- Recouvrement juridique automatisé complet.
- Comptabilité avancée.
- Connexion bancaire complète en production.
- Support offline complet.

## Niveau de fidélité attendu

Le MVP doit être crédible visuellement et fonctionnellement. Certaines intégrations peuvent être simulées mais les objets métier, statuts, permissions, données et transitions doivent être réels dans l'API.

## Definition of Done MVP

- Tous les rôles peuvent se connecter.
- Un dossier peut aller de `draft` à `active`.
- Les documents peuvent être uploadés et consultés.
- Un package financeur peut être généré.
- Une offre ferme et un contrat peuvent être générés ou simulés.
- Un actif, un échéancier, une facture et un paiement peuvent être visibles.
- Les dashboards affichent des données cohérentes.
- Les permissions empêchent les accès non autorisés.
