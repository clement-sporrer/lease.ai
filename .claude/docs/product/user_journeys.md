# User journeys

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Journey A: Revendeur crée un dossier

1. Le revendeur se connecte.
2. Il arrive sur son dashboard.
3. Il appuie sur `Nouveau dossier`.
4. Il saisit le SIREN du client.
5. LeaseAI enrichit l'entreprise.
6. Il vérifie nom, adresse, dirigeant, activité.
7. Il ajoute un devis IT.
8. LeaseAI extrait montant, matériel et fournisseur.
9. LeaseAI calcule une mensualité indicative.
10. LeaseAI affiche un score indicatif.
11. L'app liste les pièces manquantes.
12. Le revendeur upload les pièces disponibles.
13. Il soumet le dossier.
14. Il suit le statut jusqu'à décision.

## Journey B: Admin revoit un dossier

1. L'admin ouvre la queue `À revoir`.
2. Il sélectionne un dossier soumis.
3. Il lit résumé entreprise, devis, documents et score.
4. Il vérifie la checklist ADV.
5. Il demande les pièces manquantes ou pré-accorde.
6. Il génère le package financeur.
7. Il envoie ou marque le package comme transmis.
8. Il reçoit/encode la décision financeur.
9. Si accord, il génère l'offre ferme.

## Journey C: Financeur décide

1. Le financeur voit les packages assignés.
2. Il ouvre le dossier.
3. Il lit résumé entreprise, risque, pricing, actifs.
4. Il consulte les documents.
5. Il choisit `Accorder`, `Refuser`, ou `Demander clarification`.
6. La décision est tracée.
7. Le statut du deal est mis à jour.

## Journey D: PME signe et active

1. La PME reçoit une notification d'offre.
2. Elle consulte l'offre ferme.
3. Elle voit mensualité, durée, actifs, conditions clés.
4. Elle signe électroniquement.
5. Elle fournit/valide mandat SEPA.
6. Le fournisseur livre le matériel.
7. Le PV de livraison est uploadé.
8. L'ADV active le contrat.
9. La PME voit contrat, actifs, échéancier et prochaine facture.

## Journey E: Contrat actif et paiement

1. La PME ouvre `Payments`.
2. Elle voit prochaine échéance.
3. Elle consulte l'échéancier.
4. Une facture est générée.
5. Paiement reçu ou marqué reçu.
6. Le dashboard met à jour cash collecté.
7. En cas de retard, une relance est créée.

## Journey F: Renouvellement

1. À J-90, LeaseAI détecte une fin de contrat proche.
2. L'app affiche options: renouveler, prolonger, restituer.
3. L'IA suggère une action selon actif, client et marge.
4. Le revendeur ou l'ops contacte le client.
5. Un nouveau dossier ou avenant est créé.
