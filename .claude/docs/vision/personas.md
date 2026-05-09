# Personas

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Persona 1: Revendeur / apporteur

### Objectifs

- Transformer un devis IT en offre de leasing rapidement.
- Réduire les allers-retours administratifs.
- Suivre l'avancement d'un dossier.
- Savoir quoi demander au client.
- Gagner une commission ou sécuriser la vente matériel.

### Frustrations

- Délais de réponse financeur.
- Manque de visibilité sur les statuts.
- Pièces manquantes découvertes tard.
- Offres difficiles à expliquer au client.

### KPI

- Dossiers créés.
- Dossiers soumis.
- Taux d'accord.
- Temps devis -> offre indicative.
- Temps offre -> signature.
- Commission générée.

### Permissions

- Créer un dossier.
- Ajouter SIREN, devis et pièces.
- Voir ses dossiers.
- Voir statut, mensualité indicative, pièces manquantes.
- Ne peut pas modifier scoring, pricing final ou décision financeur.

## Persona 2: PME cliente / locataire

### Objectifs

- Comprendre son engagement.
- Accéder aux contrats, factures, échéanciers.
- Suivre les équipements loués.
- Préparer renouvellement ou restitution.
- Obtenir de l'aide rapidement.

### Frustrations

- Contrats difficiles à retrouver.
- Factures et paiements dispersés.
- Incertitude sur dates de prélèvement.
- Manque de visibilité sur fin de contrat.

### KPI

- Paiements à jour.
- NPS.
- Taux de renouvellement.
- Nombre d'incidents support.

### Permissions

- Voir ses contrats et actifs.
- Télécharger factures et documents.
- Voir échéancier.
- Signer ou consulter documents.
- Demander support.

## Persona 3: ADV / Ops interne

### Objectifs

- Contrôler les dossiers.
- Détecter pièces manquantes.
- Préparer le package financeur.
- Garantir la cohérence devis, contrat, mandat, livraison.
- Activer sans erreur.

### Frustrations

- Re-saisie.
- Informations incomplètes.
- Statuts flous.
- Documents mal nommés.
- Manque de traçabilité.

### KPI

- Temps de revue dossier.
- Taux de dossiers touchless.
- Nombre d'anomalies.
- Temps pré-accord -> activation.

### Permissions

- Voir tous les dossiers.
- Demander pièce.
- Pré-accorder selon règles.
- Générer package.
- Marquer accord financeur reçu.
- Préparer offre et contrat.
- Activer contrat si tous les blockers sont levés.

## Persona 4: Risk analyst / admin interne

### Objectifs

- Lire rapidement le risque.
- Comprendre les flags.
- Valider ou bloquer.
- Maintenir les règles.
- Auditer les décisions.

### KPI

- Taux d'accord.
- Taux de défaut par score band.
- Taux d'erreur décisionnelle.
- Cohérence pricing/risque.

### Permissions

- Voir scoring, règles, pricing.
- Override limité avec justification.
- Consulter audit log.
- Ne doit pas pouvoir effacer les traces.

## Persona 5: Financeur / refinanceur

### Objectifs

- Recevoir un dossier standardisé.
- Comprendre entreprise, risque, actif et pricing.
- Décider vite.
- Poser une question ou demander pièce.

### KPI

- Temps de décision.
- Taux d'accord.
- Taux de dossiers complets.

### Permissions

- Voir packages qui lui sont assignés.
- Télécharger documents.
- Répondre: accord, refus, besoin de clarification.
- Ne voit pas les données hors dossier concerné.

## Persona 6: CFO / direction

### Objectifs

- Suivre production, cash, risque, portefeuille.
- Voir rentabilité et expositions.
- Préparer reporting investisseur/refi.

### KPI

- Production mensuelle.
- Contrats actifs.
- Cash collecté.
- Retards.
- Défaut.
- Yield brut.
- Concentration partenaires/clients.

### Permissions

- Dashboards agrégés.
- Export reporting.
- Accès lecture aux dossiers.
