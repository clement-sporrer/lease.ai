# Agent architecture

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Objectif

L'IA LeaseAI réduit le coût de coordination humaine. Elle assiste, résume, extrait et recommande, mais ne décide pas seule sur les sujets financiers fermes.

## Agents MVP

### 1. Company enrichment assistant

- Résume les données entreprise.
- Signale incohérences.
- Produit une phrase simple pour l'UI.

### 2. Document extraction assistant

- Extrait lignes de devis.
- Identifie fournisseur, montant, catégories.
- Signale confiance faible.

### 3. Deal summary assistant

- Résume un dossier pour admin/risk/financeur.
- Liste les documents présents/manquants.
- Explique les flags.

### 4. Next action assistant

- Détermine la prochaine action selon statut et blockers.
- Peut rédiger un message de demande pièce.

### 5. Portfolio insight assistant

- Résume production, cash, risques.
- Identifie anomalies.

## Architecture

```txt
Mobile UI
  ↓
AI Assistant API
  ↓
Context Builder
  ↓
Policy / Decision Boundaries
  ↓
LLM Provider
  ↓
Response Validator
  ↓
Audit Log
```

## Context builder

Toujours fournir:

- rôle utilisateur;
- entité consultée;
- permissions;
- statut;
- données nécessaires seulement;
- limites de décision.

## Response validator

Bloquer:

- promesse d'accord ferme non validé;
- instruction contraire à statut;
- décision financière autonome;
- divulgation de données hors permission.
