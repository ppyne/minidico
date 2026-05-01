# Technical Architecture

## Vue d’ensemble

Le projet est organisé comme un système lexical contrôlé composé de données sources, d’un validateur et de rapports dérivés.

Les trois fichiers principaux sont :

- [wordlist_v6_2.txt](/Users/avialle/dev/minidico/versions/v6_2/wordlist_v6_2.txt)
- [dictionary_v6_2.json](/Users/avialle/dev/minidico/versions/v6_2/dictionary_v6_2.json)
- [forms_v6_2.txt](/Users/avialle/dev/minidico/versions/v6_2/forms_v6_2.txt)

Le contrôle automatique repose sur :

- [src/check_dictionary.cpp](/Users/avialle/dev/minidico/src/check_dictionary.cpp)
- [Makefile](/Users/avialle/dev/minidico/Makefile)

## Rôle des composants

### Wordlist

La `wordlist` est la source d’autorité sur le vocabulaire.

- un mot présent dans la `wordlist` doit exister dans le dictionnaire ;
- un mot absent de la `wordlist` n’a pas le droit d’apparaître dans une définition, sauf s’il est reconnu via `forms.txt` comme forme fléchie d’un lemme autorisé.

### Dictionary

Le `dictionary` contient les entrées lexicales structurées.

Chaque entrée associe :

- un lemme ;
- une catégorie grammaticale ;
- une définition textuelle.

Le dictionnaire constitue le cœur sémantique du système.

### Forms

`forms.txt` ajoute une couche morphologique explicite.

Chaque ligne suit le schéma :

```text
forme lemme
```

Exemples :

- une forme conjuguée vers un verbe ;
- un pluriel vers un nom ;
- un féminin vers un adjectif ;
- certaines contractions ou formes éditoriales, si elles sont gérées explicitement.

Le projet ne suppose pas une analyse morphologique implicite complète. La reconnaissance passe par cette table déclarative.

### Validateur

Le programme [check_dictionary](/Users/avialle/dev/minidico/check_dictionary) compile et vérifie l’ensemble.

Il s’appuie sur [src/check_dictionary.cpp](/Users/avialle/dev/minidico/src/check_dictionary.cpp) pour :

- charger la `wordlist` ;
- charger le `dictionary` ;
- charger `forms.txt` ;
- tokeniser les définitions ;
- ramener les formes vers les lemmes connus ;
- détecter les mots hors vocabulaire ;
- repérer plusieurs incohérences structurelles ;
- produire des rapports de validation.

## Flux de données

Le fonctionnement logique est le suivant :

1. lecture de la liste de mots autorisés ;
2. lecture des entrées du dictionnaire ;
3. lecture des formes fléchies reconnues ;
4. analyse de chaque définition ;
5. vérification que chaque token appartient au vocabulaire ou à une forme mappée ;
6. génération des rapports.

En pratique, les fichiers de rapports dérivent des trois sources principales plus du validateur.

## Types de fichiers

### Sources stables

- `wordlist_v*.txt`
- `dictionary_v*.json`
- `forms_v*.txt`

### Propositions intermédiaires

- `*_proposal.*`

Ces fichiers servent aux itérations avant stabilisation.

### Rapports

- `validation_report_*.md`
- `expression_validation_*.md`
- `audit_*.md`
- `weak_*.json`
- `missing_*.json`
- `diff_*.md`

Ils documentent l’état formel, qualitatif ou comparatif d’une version.

## Architecture des versions

Le projet n’écrase pas les états précédents. Chaque version stable reste disponible.

Cela permet :

- la comparaison diachronique ;
- les audits de qualité ;
- la régénération d’une branche ;
- la justification des choix éditoriaux ou lexicaux.

L’architecture globale est donc cumulative : chaque version nouvelle part d’une version stable antérieure, applique une extension ou un nettoyage, puis produit une nouvelle base stable.

## Séparation des couches

Le projet sépare clairement trois couches.

- couche lexicale : quels lemmes existent ;
- couche définitoire : comment ces lemmes sont définis ;
- couche morphologique : quelles formes de surface sont acceptées.

Cette séparation est importante car elle permet d’améliorer :

- le sens, sans changer la taille de la liste ;
- la morphologie, sans réécrire le dictionnaire ;
- la couverture conceptuelle, sans ouvrir de nouveaux domaines concrets.

## Architecture de référence

L’architecture de référence actuelle est celle de V6.2 :

- base stable à `1573` mots ;
- dictionnaire lexicalement fermé ;
- couche morphologique nettoyée ;
- validation stricte réussie ;
- tests conceptuels entièrement valides.
