# Rapport qualité V2 courte

## Portée

- La V2 courte ne modifie pas la liste des 500 mots de la V1.
- Elle réécrit uniquement 18 entrées prioritaires.
- Elle garde la fermeture lexicale stricte: 0 mot hors vocabulaire.

## Définitions retravaillées

- `femme` : `personne autre que homme` -> `personne que on nommer elle`
- `homme` : `personne autre que femme` -> `personne que on nommer il`
- `bon` : `avec qualité utile ou de bien` -> `avec qualité qui aider une personne ou une chose`
- `mauvais` : `avec effet de mal ou de problème` -> `avec effet qui faire mal ou problème`
- `bien` : `de manière bon` -> `de manière utile ou avec bon effet`
- `mal` : `de manière mauvais` -> `de manière qui faire problème ou douleur`
- `vrai` : `avec vérité` -> `qui représenter bien ce qui est`
- `faux` : `sans vérité ou contre vérité` -> `qui ne représenter pas bien ce qui est`
- `haut` : `avec place vers ciel` -> `avec place loin de sol`
- `bas` : `avec place vers sol` -> `avec place près de sol`
- `proche` : `avec peu de distance` -> `avec peu de distance entre une chose ou personne et une autre`
- `loin` : `avec grand distance` -> `avec beaucoup de distance entre une chose ou personne et une autre`
- `rapide` : `pas lent` -> `avec peu de temps pour une action ou un mouvement`
- `lent` : `pas rapide` -> `avec beaucoup de temps pour une action ou un mouvement`
- `faire` : `produire une action` -> `produire ou former une action un effet ou une chose`
- `action` : `fait de faire` -> `ce que une personne ou une chose faire`
- `de` : `mot pour relation` -> `mot pour montrer une relation entre chose personne action ou partie`
- `ou` : `mot pour choix` -> `mot pour montrer un choix entre une chose et une autre`

## Gains qualitatifs

- `homme` et `femme` ne se définissent plus l un par l autre.
- `rapide` et `lent` ne sont plus définis par simple négation mutuelle.
- `haut` et `bas` s ancrent maintenant sur `sol`, ce qui réduit l opposition pure.
- `vrai` et `faux` passent d une relation pauvre avec `vérité` à une relation plus descriptive via `représenter` et `ce qui est`.
- `faire` et `action` restent liés, mais de façon moins pauvre qu en V1.
- `de` et `ou` sont rendus plus utiles comme mots grammaticaux structurants.

## Limites restantes

- La circularité indirecte profonde reste forte dans le système global, car cette V2 courte n agit que sur 18 entrées.
- Certains mots abstraits (`bon`, `mauvais`, `bien`, `mal`, `vrai`, `faux`) restent difficiles à stabiliser sans enrichir encore la métalangue.
- `de` et `ou` sont plus explicites, mais restent forcément métalinguistiques et très centraux.

## Entrées encore sensibles

- `haut` : definition_still_compact, relational_scale_word, indirect_cycle
- `bas` : definition_still_compact, relational_scale_word, indirect_cycle
- `femme` : definition_still_compact, social_core_word, indirect_cycle
- `homme` : definition_still_compact, social_core_word, indirect_cycle
- `de` : grammatical_core_word, indirect_cycle
- `ou` : grammatical_core_word, indirect_cycle
- `faire` : core_action_pair, indirect_cycle
- `action` : core_action_pair, indirect_cycle
- `proche` : relational_scale_word, indirect_cycle
- `loin` : relational_scale_word, indirect_cycle
- `mal` : abstract_core_word, indirect_cycle
- `mauvais` : abstract_core_word, indirect_cycle
- `bon` : abstract_core_word
- `bien` : abstract_core_word
- `vrai` : abstract_core_word
- `faux` : abstract_core_word
- `rapide` : relational_scale_word
- `lent` : relational_scale_word
