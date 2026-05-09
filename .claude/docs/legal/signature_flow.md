# Signature flow

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

Envoyer, suivre et archiver une signature électronique.

## MVP mock

Étapes:

1. Génération contrat.
2. `Send for signature`.
3. Statut `signing`.
4. Bouton admin `Simuler signature`.
5. Création document signé mock.
6. Statut `signed`.

## Production

Étapes:

1. Créer enveloppe signature.
2. Envoyer au signataire.
3. Recevoir webhook.
4. Vérifier complétion.
5. Télécharger document signé.
6. Stocker preuve.
7. Passer statut contrat à `signed`.

## UI

Afficher:

- destinataire;
- statut;
- date envoi;
- date signature;
- document;
- preuve si disponible.

## Blockers

- Signataire manquant.
- Email signataire manquant.
- Contrat non généré.
- Accord financeur absent.

## Audit

- signature.created;
- signature.sent;
- signature.viewed si dispo;
- signature.completed;
- signature.failed.
