# Rapport qualité V1

## Résumé

- Taille du vocabulaire V1: 500 mots.
- Remplacements appliqués: 50 sorties et 50 entrées.
- Définitions exactement égales à `faire`: 0 (contre 97 en V0).
- Définitions exactement égales à `mot simple`: 0 (contre 94 en V0).
- Mots hors vocabulaire dans les définitions: 0.
- Circularités directes simples: 0.
- Entrées encore signalées comme faibles: 317.

## Gains principaux

- Tous les verbes auparavant réduits à `faire` ont reçu une définition orientée action, état, relation, mouvement ou information.
- Toutes les entrées auparavant réduites à `mot simple` ont été réécrites.
- Le noyau `mot / faire / partie / temps / simple / autre / même` a été réécrit avec un vocabulaire plus structurant.
- La V1 reste à 500 mots et ne passe pas à 750.

## Faiblesses restantes

- Un grand noyau de circularité indirecte subsiste, surtout via les mots structurants très fréquents (`de`, `une`, `pour`, `ou`, `chose`, `avec`).
- Certains mots fondamentaux restent difficiles à définir sans opposition ou sans appui mutuel, en particulier `homme`, `femme`, `bon`, `mauvais`, `bien`, `mal`, `vrai`, `faux`.
- Quelques définitions sont encore courtes ou schématiques, mais elles sont nettement plus informatives qu en V0.

## Mots structurants en V1

- `de` : 174 définitions dépendantes
- `une` : 146 définitions dépendantes
- `pour` : 132 définitions dépendantes
- `ou` : 127 définitions dépendantes
- `chose` : 88 définitions dépendantes
- `un` : 80 définitions dépendantes
- `avec` : 64 définitions dépendantes
- `dans` : 55 définitions dépendantes
- `personne` : 48 définitions dépendantes
- `partie` : 47 définitions dépendantes
- `mot` : 46 définitions dépendantes
- `faire` : 42 définitions dépendantes

## Plus grandes composantes de circularité indirecte

- taille 194 : action, aller, animal, appartenir, après, article, au, aucun, aussi, autre, avant, avec, avoir, beaucoup, besoin, but, cause, ce, changer, chemin ...
- taille 4 : boire, bouche, eau, manger
- taille 3 : bien, bon, utile
- taille 3 : bruit, entendre, oreille
- taille 2 : acheter, argent
- taille 2 : assez, trop
- taille 2 : bas, sol
- taille 2 : bouger, mouvement

## Entrées à retravailler d abord en V2 courte

- `femme` : contrastive_definition_family, indirect_cycle, mutual_definition_pair, semantic_precision_still_limited
- `homme` : contrastive_definition_family, indirect_cycle, mutual_definition_pair, semantic_precision_still_limited
- `mal` : contrastive_definition_family, definition_still_short, indirect_cycle
- `loin` : contrastive_definition_family, definition_still_short, indirect_cycle
- `haut` : contrastive_definition_family, indirect_cycle
- `proche` : contrastive_definition_family, indirect_cycle
- `mauvais` : contrastive_definition_family, indirect_cycle
- `bien` : contrastive_definition_family, definition_still_short, indirect_cycle
- `vrai` : definition_still_short, indirect_cycle, semantic_precision_still_limited
- `rapide` : contrastive_definition_family, definition_still_short, indirect_cycle
- `lent` : contrastive_definition_family, definition_still_short, indirect_cycle
- `de` : definition_still_short, indirect_cycle
- `ou` : definition_still_short, indirect_cycle
- `faire` : definition_still_short, indirect_cycle
- `action` : definition_still_short, indirect_cycle
