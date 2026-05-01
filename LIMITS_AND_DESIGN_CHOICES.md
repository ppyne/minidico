# Limits And Design Choices

## Vocabulaire contrôlé

- Le dictionnaire reste fermé et explicitement vérifiable.
- Les définitions privilégient la clarté et la fermeture lexicale plutôt que la précision encyclopédique.

## Mots quasi primitifs

- Certains mots servent de pivots : `chose`, `personne`, `faire`, `temps`, `document`, `travail`, `animal`, `plante`, `art`, `science`.

## Formes fléchies

- Les formes restent explicites dans les fichiers `forms_vX.txt`.
- Aucune lemmatisation implicite n est supposée.

## Nombres

- Les nombres fondamentaux sont intégrés comme mots du dictionnaire.
- Les chiffres numériques `0-9` peuvent être admis comme symboles externes dans les tests, mais les définitions restent textuelles.

## Polysémies

- Certaines polysémies sont conservées si elles restent courantes et lisibles, par exemple `accord`, `feu`, `voie`, `port`.

## Limites sectorielles

- Le médical reste informatif et non prescriptif.
- Le juridique reste courant et non spécialisé.
- Le scientifique reste introductif.
- Le corpus ne remplace pas la langue naturelle complète.
