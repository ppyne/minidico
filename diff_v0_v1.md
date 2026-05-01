# Diff V0 / V1

## Résumé quantitatif

- V0: 500 mots, V1: 500 mots.
- Remplacements de vocabulaire: 50 sorties / 50 entrées.
- Définitions changées sur mots conservés: 358.
- `faire` seul: 97 -> 0.
- `mot simple` seul: 94 -> 0.
- Mots hors vocabulaire: 0 -> 0.
- Circularités directes simples: 0 -> 0 sur les fichiers validés de chaque version.

## 50 mots retirés

- ami, voisin, midi, lune, étoile, neige, glace, rivière, lac, montagne, forêt, cheval, vache, pont, village, région, coin, science, art, danse, chant, film, classe, bureau, magasin, marché, usine, jardin, cuisine, repas, fruit, légume, viande, lait, sucre, sel, huile, tasse, verre, bouteille, vêtement, robe, pantalon, chemise, chaussure, clé, sac, bateau, avion, radio

## 50 mots ajoutés

- manière, action, mouvement, objet, matière, plante, bruit, espace, contact, direction, distance, place, surface, point, ensemble, relation, état, fonction, valeur, quantité, qualité, sorte, genre, reste, devenir, produire, permettre, appartenir, contenir, former, signifier, représenter, exister, placer, occuper, résultat, différence, ressemblance, sentiment, émotion, grandir, communiquer, information, comparer, décrire, nommer, article, pronom, verbe, adjectif

## Réécritures centrales

- `être`
  V0: `mot simple`
  V1: `verbe pour exister ou pour dire un état`
- `avoir`
  V0: `mot simple`
  V1: `verbe pour recevoir garder ou contenir`
- `faire`
  V0: `mot simple`
  V1: `produire une action`
- `mot`
  V0: `partie de langue`
  V1: `signe de langue avec un sens`
- `partie`
  V0: `chose dans une chose`
  V1: `chose dans un ensemble`
- `temps`
  V0: `mot simple`
  V1: `ensemble de moment entre avant et après`
- `simple`
  V0: `pas difficile`
  V1: `avec peu de partie et peu de problème`
- `autre`
  V0: `pas le même`
  V1: `différent de ce qui est là`
- `même`
  V0: `pas autre`
  V1: `sans différence`
- `dire`
  V0: `faire`
  V1: `communiquer par mot ou par voix`
- `voir`
  V0: `faire`
  V1: `recevoir une image par œil`
- `penser`
  V0: `faire`
  V1: `former une idée dans esprit`
- `parler`
  V0: `faire`
  V1: `communiquer par la voix`
- `question`
  V0: `mot pour demander`
  V1: `phrase pour demander une information`
- `réponse`
  V0: `mot pour répondre`
  V1: `information ou phrase pour répondre à une question`
- `langue`
  V0: `groupe de mot pour parler`
  V1: `ensemble de mot et de règle pour parler`
- `forme`
  V0: `partie de image`
  V1: `manière de être dans espace`
- `usage`
  V0: `fait de utiliser`
  V1: `fonction de une chose`
- `problème`
  V0: `chose difficile`
  V1: `chose difficile pour une action ou une réponse`
- `solution`
  V0: `réponse de problème`
  V1: `réponse ou action pour finir un problème`

## Interprétation

- La V1 est une amélioration contrôlée: elle garde la taille maximale à 500 mots, ferme complètement le vocabulaire et remplace les définitions placeholders par des gloses plus discriminantes.
- Le gain principal est qualitatif sur les verbes, la métalangue et les mots grammaticaux.
- Le gain reste partiel sur les notions très abstraites ou très primitives, qui demanderaient encore une V2 courte ciblée.
