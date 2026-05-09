# Decision boundaries

> Projet: LeaseAI mobile app MVP complet  
> Positionnement: AI-native IT leasing operator  
> Usage: document source-of-truth pour product, design, mobile, backend, risk, ops et demo.

## Limites non négociables

L'IA ne peut jamais:

- donner un accord ferme de financement;
- refuser définitivement un dossier;
- modifier le pricing final;
- modifier un score sans validation humaine;
- activer un contrat;
- marquer un paiement reçu;
- signer un document;
- masquer un document ou un audit event;
- générer une promesse juridique non validée.

## L'IA peut

- résumer;
- expliquer;
- extraire;
- classer;
- proposer;
- rédiger une demande pièce;
- détecter une incohérence;
- recommander une prochaine action;
- préparer une checklist.

## Niveaux de confiance

### High confidence

L'IA peut afficher un résumé direct.

### Medium confidence

L'IA doit indiquer les limites et proposer vérification.

### Low confidence

L'IA doit demander revue humaine.

## Audit

Toute réponse IA liée à un deal doit être associée à:

- user_id;
- deal_id;
- prompt template version;
- context hash;
- response;
- timestamp.
