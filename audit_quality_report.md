# Audit qualitatif de la V0

## Synthèse

- La V0 est formellement valide, mais sa qualité explicative est faible sur une grande partie du lexique.
- 97 verbes sont reduits a la seule glose `faire`.
- 94 entrees sont reduites a la seule glose `mot simple`.
- 21 composantes de circularite indirecte de taille > 1 ont ete detectees.
- 50 mots apparaissent comme de bons candidats de sortie pour une V1 a taille constante.
- 50 mots absents sont proposes pour augmenter fortement la puissance definitoire sans agrandir la liste.

## 1. Definitions trop vagues

La faiblesse principale de la V0 n est pas la fermeture lexicale mais la perte de contraste semantique.
Les cas les plus problematiques sont :
- les verbes definis uniquement par `faire` ;
- les mots grammaticaux defines par `mot simple` ;
- les noms concrets maintenus par simple presence de categorie, sans traits distinctifs ;
- les adjectifs definis seulement par opposition binaire (`pas X`, `comme Y`).

Exemples de definitions trop vagues :
- `aller` : `faire`
- `voir` : `faire`
- `dire` : `faire`
- `penser` : `faire`
- `ami` : `mot simple`
- `radio` : `mot simple`
- `classe` : `mot simple`
- `science` : `mot simple`
- `chaussure` : `mot simple`
- `bouteille` : `mot simple`

## 2. Circularites indirectes

Les circularites ne rendent pas la V0 invalide, mais elles ralentissent fortement l apprentissage du systeme.
Composantes les plus visibles :
- taille 28 : après, autre, avec, but, chose, dans, de, dernier, difficile, facile, faire, fin, groupe, intérieur, langue, le, mot, même, parler, partie, pas, pour, simple, temps, un, une, vouloir, à
- taille 3 : beaucoup, peu, plus
- taille 3 : mesure, poids, taille
- taille 2 : ancien, nouveau
- taille 2 : assez, trop
- taille 2 : avant, premier
- taille 2 : bas, haut
- taille 2 : bien, mal

Le noyau le plus lourd tourne autour de `mot`, `simple`, `faire`, `partie`, `temps`, `pour`, `dans`, `autre`, `même`.
Ce n est pas une circularite tautologique directe, mais un cycle d appui mutuel trop pauvre.

## 3. Definitions par quasi-equivalence

Plusieurs entrees sont grammaticalement acceptables mais peu informatives, car elles ne font que pointer vers un contraire, un voisin semantique ou une paraphrase minimale.
- `bon` / `mauvais`
- `bien` / `mal`
- `haut` / `bas`
- `nouveau` / `ancien`
- `plein` / `vide`
- `sec` / `humide`
- `proche` / `loin`
- `court` / `long`
- `aussi` / `même`
- `ainsi` / `même`

Ces paires ne sont pas toutes mauvaises en soi, mais elles deviennent faibles lorsqu elles ne sont pas contrebalancees par une definition positive ailleurs.

## 4. Entrees grammaticalement correctes mais peu utiles

La V0 contient des mots legitimes du francais simple, mais certains ont une faible rentabilite definitoire : ils n aident presque aucune autre entree et n ameliorent pas la metalangue interne.
Exemples typiques :
- `radio` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `film` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `chant` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `danse` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `robe` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `pantalon` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `chaussure` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `tasse` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `bouteille` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.
- `midi` : score faible, peu de dependances entrantes, faible rendement pour la definition des autres mots.

## 5. Classement par utilite reelle

Le fichier `word_utility_ranking.csv` classe les 500 mots selon un score combinant :
- role grammatical ou structural ;
- nombre de definitions qui dependent du mot ;
- richesse de la definition actuelle ;
- appartenance au noyau d axiomes ;
- penalite pour les placeholders et pour les mots proposes a la sortie.

Top 15 des mots les plus utiles en V0 :
- `avec` (grammaire) : score 119.2
- `dans` (grammaire) : score 118.4
- `mot` (nom) : score 118.4
- `pour` (grammaire) : score 118.4
- `faire` (verbe) : score 113.6
- `partie` (nom) : score 113.4
- `personne` (nom) : score 111.6
- `de` (grammaire) : score 105.6
- `pas` (grammaire) : score 105.6
- `ou` (grammaire) : score 105.2
- `chose` (nom) : score 103.6
- `autre` (grammaire) : score 102.0
- `qui` (grammaire) : score 102.0
- `temps` (nom) : score 101.2
- `lieu` (nom) : score 98.0

Bottom 15 des mots les moins utiles en V0 :
- `marché` (nom) : score 13.6
- `pantalon` (nom) : score 13.6
- `radio` (nom) : score 13.6
- `repas` (nom) : score 13.6
- `robe` (nom) : score 13.6
- `sac` (nom) : score 13.6
- `science` (nom) : score 13.6
- `sel` (nom) : score 13.6
- `sucre` (nom) : score 13.6
- `tasse` (nom) : score 13.6
- `usine` (nom) : score 13.6
- `verre` (nom) : score 13.6
- `viande` (nom) : score 13.6
- `voisin` (nom) : score 13.6
- `vêtement` (nom) : score 13.6

## 6. Les 50 mots les moins necessaires

Liste proposee pour sortie en V1 :
- radio, film, chant, danse, art, science, bureau, usine, marché, magasin, jardin, cuisine, tasse, verre, bouteille, robe, pantalon, chemise, chaussure, bateau, avion, cheval, vache, fruit, légume, viande, lait, sucre, sel, huile, vêtement, classe, coin, région, village, repas, clé, sac, pont, forêt, montagne, lac, rivière, neige, glace, étoile, lune, midi, voisin, ami

## 7. Les 50 mots qui manquent le plus

Liste proposee pour entree en V1 :
- manière, action, mouvement, objet, matière, plante, bruit, espace, contact, direction, distance, place, surface, point, ensemble, relation, état, fonction, valeur, quantité, qualité, sorte, genre, reste, devenir, produire, permettre, appartenir, contenir, former, signifier, représenter, exister, placer, occuper, résultat, différence, ressemblance, sentiment, émotion, grandir, communiquer, information, comparer, décrire, nommer, article, pronom, verbe, adjectif

## 8. Proposition de V1 a taille constante

Principe : ne pas monter a 750 mots tout de suite. Remplacer 50 mots concrets peu structurants par 50 mots de metalangue et de description generale.
Effets attendus :
- meilleures definitions de verbes ;
- meilleures definitions des mots grammaticaux ;
- reduction des cycles pauvres ;
- possibilite de passer de `faire` / `mot simple` a des definitions plus contrastives.

Exemples de remplacements structurants :
- `radio` -> `manière`
- `film` -> `action`
- `chant` -> `mouvement`
- `danse` -> `objet`
- `art` -> `matière`
- `science` -> `plante`
- `bureau` -> `bruit`
- `usine` -> `espace`
- `marché` -> `contact`
- `magasin` -> `direction`
- `jardin` -> `distance`
- `cuisine` -> `place`
- `tasse` -> `surface`
- `verre` -> `point`
- `bouteille` -> `ensemble`

Les details sont fournis dans `replacement_candidates.json`, `dictionary_v1_proposal.json` et `wordlist_v1_proposal.txt`.
