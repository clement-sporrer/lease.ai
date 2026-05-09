# Design decisions log

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Utilisation

Ce fichier doit être mis à jour à chaque décision produit/design importante. Il évite de rouvrir les mêmes débats.

## Template

```md
### YYYY-MM-DD - Titre décision

**Décision**  
...

**Pourquoi**  
...

**Alternatives rejetées**  
...

**Impact**  
...

**Owner**  
...
```

## Décisions initiales

### 2026-04-26 - App mobile multi-rôles

**Décision**  
Construire une app mobile multi-rôles plutôt que plusieurs apps séparées.

**Pourquoi**  
Le cycle de leasing traverse plusieurs parties prenantes mais les objets métier sont les mêmes. Une app unifiée accélère le développement et la cohérence UX.

**Alternatives rejetées**  
Apps séparées pour revendeur, client, admin et financeur.

**Impact**  
Nécessité d'un RBAC strict et d'une navigation conditionnelle.

### 2026-04-26 - Statuts métier au centre de l'UX

**Décision**  
Toutes les pages de dossier/contrat affichent le statut et la prochaine action.

**Pourquoi**  
Le principal problème utilisateur est l'incertitude sur l'avancement et les blockers.

**Impact**  
Besoin d'une status machine claire côté backend.

### 2026-04-26 - IA assistante, pas décideuse

**Décision**  
L'IA résume, explique et recommande, mais ne donne pas d'accord ferme.

**Pourquoi**  
Crédibilité risk/compliance et nécessité d'une gouvernance humaine.

**Impact**  
Les prompts doivent inclure des limites explicites.
