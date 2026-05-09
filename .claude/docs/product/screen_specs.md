# Screen specs

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## SCR-AUTH-001 Login

### Objectif

Connecter un utilisateur et charger son rôle principal.

### Contenu

- Logo LeaseAI.
- Email.
- Mot de passe.
- CTA `Log in`.
- Lien `Forgot password`.
- Option `SSO Login` en mode mock.

### États

- Empty.
- Loading.
- Error credentials.
- Error network.
- Success redirect.

### API

- `POST /auth/login`
- `GET /me`

## SCR-PARTNER-001 Partner dashboard

### Objectif

Donner au revendeur une vue immédiate de son pipeline.

### KPIs

- Dossiers actifs.
- Engagement total.
- Dossiers à compléter.
- Dossiers approuvés.
- Commission estimée.

### Sections

- Greeting.
- Health banner.
- KPI cards.
- Recent activity.
- CTA `Nouveau dossier`.

## SCR-PARTNER-003 Create deal - SIREN

### Objectif

Créer la base d'un dossier en partant du SIREN.

### Champs

- SIREN/SIRET.
- Nom commercial optionnel.
- Contact client optionnel.

### Validation

- 9 chiffres pour SIREN.
- 14 chiffres pour SIRET.
- Pas de caractères non numériques.

### CTA

`Enrichir l'entreprise`.

## SCR-PARTNER-004 Company enrichment

### Objectif

Afficher les données entreprise récupérées.

### Contenu

- Raison sociale.
- SIREN/SIRET.
- Adresse.
- Activité.
- Date de création.
- Dirigeant si disponible.
- Statut actif.
- Alertes: société récente, radiation, incohérence.

### CTA

`Confirmer et continuer`.

## SCR-PARTNER-005 Quote upload

### Objectif

Ajouter le devis IT.

### Contenu

- Upload PDF/image.
- Résultat extraction.
- Montant HT/TTC.
- Fournisseur.
- Catégorie matériel.
- Liste lignes principales.

### États

- Uploading.
- Extracting.
- Extraction failed.
- Manual edit.

## SCR-PARTNER-006 Indicative offer

### Objectif

Présenter une mensualité indicative claire.

### Contenu

- Montant financé.
- Durée.
- Mensualité indicative.
- Fréquence.
- Hypothèses.
- Disclaimer accord indicatif.

### CTA

`Voir le score` puis `Soumettre le dossier` si conditions remplies.

## SCR-ADMIN-003 Deal review

### Objectif

Permettre à l'ADV/risk de décider la prochaine action.

### Contenu

- Header statut.
- Résumé entreprise.
- Devis.
- Score.
- Pricing.
- Documents.
- Timeline.
- Checklist.
- Audit events.

### Actions

- Demander pièce.
- Pré-accorder.
- Refuser.
- Générer package financeur.

## SCR-ADMIN-011 Activation checklist

### Objectif

Empêcher l'activation avant conformité minimale.

### Conditions obligatoires

- Accord financeur reçu.
- Offre ferme générée.
- Contrat signé.
- Mandat SEPA reçu ou simulé validé.
- PV livraison reçu.
- Actif créé.
- Échéancier généré.

### CTA

`Activer le contrat` uniquement si tous les blockers sont levés.

## SCR-CLIENT-002 Lease overview

### Objectif

Donner à la PME une vision de son contrat actif.

### Contenu

- Client.
- Statut actif.
- Lease ID.
- Date de début.
- Date de fin.
- Engagement total.
- Prochain paiement.
- Health score.
- Actifs associés.
- Documents.

## SCR-CFO-001 Portfolio dashboard

### Objectif

Afficher la performance globale.

### KPIs

- Production mensuelle.
- Contrats actifs.
- Total commitment.
- Cash collecté.
- Paiements en retard.
- Taux de rejet.
- Taux de renouvellement.
- Exposition par partenaire.

## SCR-SHARED-002 AI Assistant

### Objectif

Répondre à des questions contextuelles et recommander la prochaine action.

### Exemples de questions

- Où en est le dossier Globex ?
- Quelle pièce manque ?
- Pourquoi le score est orange ?
- Peut-on générer l'offre ferme ?
- Quel est le prochain paiement ?

### Limite

L'assistant n'approuve jamais seul un dossier.
