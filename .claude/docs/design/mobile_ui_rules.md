# Mobile UI rules

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## 1. Thumb-friendly actions

Les CTA principaux doivent être accessibles dans la zone basse de l'écran quand l'action est critique. Utiliser des sticky bottom actions pour:

- soumission de dossier;
- génération package;
- décision financeur;
- activation contrat;
- signature.

## 2. KPI cards lisibles

Une carte KPI mobile doit contenir:

- label court;
- valeur principale;
- variation ou statut;
- éventuellement une icône.

Maximum deux KPI côte à côte sur mobile.

## 3. Timelines verticales

Les étapes de dossier doivent être en timeline verticale sur mobile, pas en frise horizontale complexe.

## 4. Financial hierarchy

Pour une mensualité:

1. Montant mensuel.
2. Durée.
3. Montant financé.
4. Hypothèses.
5. Disclaimer.

## 5. Empty states actionnables

Un écran vide doit indiquer:

- ce qui manque;
- pourquoi c'est utile;
- action suivante.

Exemple:

> Aucun devis ajouté. Ajoutez le devis IT pour calculer une mensualité indicative.

## 6. Loading states crédibles

Pour enrichissement et extraction:

- montrer les étapes;
- éviter spinner seul;
- afficher progression textuelle.

Exemple:

```txt
Recherche entreprise
Analyse activité
Vérification statut
Préparation score indicatif
```

## 7. Modales rares

Utiliser les modales uniquement pour confirmations sensibles:

- refus dossier;
- override score/pricing;
- activation contrat;
- décision financeur.

## 8. Toasts sobres

Succès: court, vert.  
Erreur: explicite, action possible.  
Jamais de toast pour information critique durable.
