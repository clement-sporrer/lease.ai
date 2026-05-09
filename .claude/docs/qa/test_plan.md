# Test plan

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Tests critiques MVP

### Auth

- Login valide.
- Login invalide.
- Session expirée.
- Rôle unique.
- Multi-rôles.

### Permissions

- Partner ne voit que ses dossiers.
- Client ne voit que ses contrats.
- Financier ne voit que ses packages.
- Admin voit queue.
- Actions interdites bloquées API.

### Deal flow

- Créer dossier.
- Enrichir entreprise.
- Ajouter devis.
- Calculer mensualité.
- Calculer score.
- Soumettre.
- Revue admin.
- Demande pièce.
- Pré-accord.
- Package financeur.
- Décision financeur.
- Offre ferme.
- Contrat.
- Signature mock.
- Activation.

### Documents

- Upload PDF.
- Rejet type invalide.
- Téléchargement autorisé.
- Téléchargement interdit.
- Versioning.

### Billing

- Générer échéancier.
- Générer facture.
- Marquer paiement.
- Afficher client.
- Afficher CFO.

### AI assistant

- Résumer deal.
- Expliquer statut.
- Refuser décision ferme.
- Respecter permissions.

## Tests E2E prioritaires

1. Partner crée dossier complet -> admin approuve -> financeur approuve -> contrat actif.
2. Partner crée dossier incomplet -> admin demande pièce -> partner ajoute -> reprise.
3. Client consulte contrat actif -> voit échéancier -> télécharge facture.
4. Admin tente activation sans mandat -> bloqué.
5. Financier ne peut pas voir package non assigné.
