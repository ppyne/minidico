# Validation Method

## Principe général

La validation du projet vérifie qu’un dictionnaire à vocabulaire fermé reste cohérent sur trois plans :

- lexical ;
- structurel ;
- expressif.

Le but n’est pas seulement de posséder une liste de mots. Il faut aussi s’assurer que les définitions n’utilisent pas de vocabulaire externe, que les entrées sont complètes et que le corpus permet réellement d’écrire des phrases contrôlées.

## Entrées de validation

La validation s’appuie au minimum sur :

- une `wordlist` ;
- un `dictionary` ;
- un `forms.txt`.

Pour V6.2, les fichiers de référence sont :

- [wordlist_v6_2.txt](/Users/avialle/dev/minidico/versions/v6_2/wordlist_v6_2.txt)
- [dictionary_v6_2.json](/Users/avialle/dev/minidico/versions/v6_2/dictionary_v6_2.json)
- [forms_v6_2.txt](/Users/avialle/dev/minidico/versions/v6_2/forms_v6_2.txt)

## Validation stricte

La validation stricte est réalisée par [check_dictionary](/Users/avialle/dev/minidico/check_dictionary).

Elle contrôle notamment :

- le nombre de mots dans la liste ;
- le nombre d’entrées dans le dictionnaire ;
- l’existence d’une entrée pour chaque mot ;
- l’absence d’entrées hors liste ;
- l’absence de doublons dans la liste ;
- l’absence de définitions vides ;
- la présence des catégories grammaticales ;
- l’absence de mots hors vocabulaire dans les définitions ;
- l’absence de circularités directes simples ;
- certains problèmes d’apostrophes.

Le rapport principal produit est un `validation_report`.

## Rôle de forms.txt dans la validation

La validation ne regarde pas seulement les lemmes nus. Elle accepte aussi des formes de surface si elles sont explicitement déclarées dans `forms.txt`.

Exemple logique :

- si `parlent -> parler` existe dans `forms.txt`, alors `parlent` peut apparaître dans une définition ou un test ;
- si la forme n’est pas déclarée, elle peut être rejetée même si son lemme fait partie du vocabulaire.

Cette méthode rend la validation stricte, reproductible et explicite.

## Validation d’expression

Le projet ajoute des batteries de phrases de test.

Le principe est le suivant :

1. écrire des phrases ciblées par domaine ou par fonction ;
2. vérifier qu’elles n’emploient que des mots autorisés ou des formes autorisées ;
3. classer les phrases selon leur qualité :
   - naturelle ;
   - acceptable ;
   - lourde ;
   - impossible.

La validation d’expression ne remplace pas la validation stricte. Elle la complète. Une version peut être formellement correcte tout en restant peu expressive ou trop artificielle.

## Validation qualitative

En plus du contrôle formel, le projet utilise des audits qualitatifs.

Les audits cherchent notamment :

- des définitions trop courtes ;
- des hyperonymes seuls ;
- des définitions de type `chose de ...` ou `chose pour ...` ;
- des définitions mutuellement pauvres ;
- des accords douteux ;
- des formes morphologiques suspectes ;
- des phrases conceptuelles trop lourdes.

Cette couche qualitative explique pourquoi une version plus récente peut être meilleure sans forcément ajouter beaucoup de mots.

## Stabilisation d’une version

Une proposition ne devient stable qu’après une nouvelle validation sur les fichiers copiés sous leur nom définitif.

La méthode de stabilisation suit généralement ce cycle :

1. produire une proposition ;
2. valider la proposition ;
3. corriger les problèmes détectés ;
4. copier vers les noms stables ;
5. relancer la validation finale ;
6. produire les rapports finaux et le README de version.

Cette séparation entre proposition et version stable évite de figer un état non vérifié.

## Critères de réussite typiques

Pour les versions récentes, les critères de réussite sont généralement :

- `0` mot hors vocabulaire ;
- `0` circularité directe simple ;
- une couverture de tests satisfaisante ;
- une baisse des formulations lourdes ;
- une couche morphologique propre ;
- une cohérence éditoriale suffisante pour stabilisation.

## Résultat V6.2

La méthode de validation aboutit, pour V6.2 stable, à :

- `1573/1573` définitions conformes ;
- `0` mot hors vocabulaire ;
- `0` circularité directe simple ;
- `300/300` phrases conceptuelles valides ;
- `0` phrase impossible ;
- `0` phrase lourde.

V6.2 est donc la version de référence non seulement parce qu’elle est plus large, mais parce qu’elle a aussi passé le cycle complet de validation formelle, morphologique, éditoriale et conceptuelle.

## Commandes utiles

Validation standard :

```sh
make
./check_dictionary
```

Selon la version que l’on veut contrôler, on place temporairement les fichiers ciblés sous les noms attendus par le validateur, ou on utilise un répertoire de travail dédié avec :

- `wordlist.txt`
- `dictionary.json`
- `forms.txt`

Cette convention simple rend la validation facile à reproduire.
