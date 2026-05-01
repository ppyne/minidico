# Project Overview

## But du projet

Ce projet construit un dictionnaire français contrôlé à vocabulaire fermé.

L’idée centrale est simple : définir chaque mot avec d’autres mots du même corpus, de manière vérifiable automatiquement. Le projet cherche donc un équilibre entre trois objectifs :

- disposer d’une liste de mots limitée mais utile ;
- maintenir une fermeture lexicale stricte ;
- produire un français assez naturel pour définir, expliquer, raisonner et s’exprimer simplement.

Le résultat n’est pas un dictionnaire général du français. C’est un système lexical contrôlé, conçu pour être cohérent, auditable et exploitable par des humains comme par des outils.

## Trois fichiers centraux

Le projet repose sur trois artefacts différents.

- `wordlist` : la liste officielle des lemmes autorisés. Elle définit le périmètre du vocabulaire.
- `dictionary` : l’ensemble des entrées lexicales, avec pour chaque lemme une catégorie grammaticale et une définition.
- `forms.txt` : la table explicite des formes fléchies ou variantes reconnues pendant la validation, avec une correspondance `forme -> lemme`.

Autrement dit :

- la `wordlist` dit quels mots existent dans le système ;
- le `dictionary` dit ce que ces mots veulent dire ;
- `forms.txt` dit quelles formes réelles du français sont acceptées comme variantes de ces mots.

## Évolution de V0 à V6.2

Le projet a progressé par étapes successives.

- `V0` : première base fermée de `500` mots, formellement valide mais encore sémantiquement pauvre.
- `V1` : réécriture des définitions les plus faibles sans augmenter la taille.
- `V2` : amélioration ciblée des définitions centrales.
- `V2.1` : enrichissement morphologique via `forms.txt`.
- `V2.2` : ajout pragmatique minimal pour la vie courante.
- `V3.0` et `V3.1` : extension santé, biologie, médecine simple et santé reproductive.
- `V3.2` et `V3.3` : extension vers travail, administration, argent, droit courant, logement et santé plus fine.
- `V4.0` à `V4.6` : ouverture contrôlée vers le monde physique, les nombres, la nature, l’alimentation, le transport, les sciences simples, l’art et la culture.
- `V5` : consolidation en corpus confortable autour de `1500` mots.
- `V5.1` et `V5.2` : amélioration éditoriale et sémantique des définitions existantes.
- `V6.0` : extension conceptuelle pour mieux définir, comparer, argumenter, évaluer et nuancer.
- `V6.1` : audit qualité grammatical, morphologique et conceptuel.
- `V6.2` : stabilisation éditoriale et conceptuelle légère, avec nettoyage morphologique ciblé.

## Pourquoi V6.2 est la version de référence

V6.2 est la meilleure synthèse actuelle du projet.

- elle conserve une taille encore contrôlable : `1573` mots ;
- elle garde une fermeture lexicale stricte ;
- elle corrige des accords et des formulations faibles repérés par les audits ;
- elle ajoute seulement `12` concepts transversaux utiles, sans ouvrir de nouveau domaine concret ;
- elle nettoie les formes orthographiques fautives ciblées dans la couche morphologique ;
- elle conserve `300/300` tests conceptuels valides, avec `0` phrase impossible et `0` phrase lourde.

V6.2 n’est donc pas seulement une extension. C’est la première version à la fois large, stable, conceptuellement utile et éditorialement plus propre.

## Critères de validation

Le projet utilise des critères formels et des critères d’usage.

Critères formels :

- chaque mot de la `wordlist` doit avoir une entrée dans le dictionnaire ;
- aucune entrée ne doit utiliser un mot hors vocabulaire ;
- les catégories grammaticales doivent être présentes ;
- les définitions vides sont interdites ;
- les doublons de la liste sont interdits ;
- les circularités directes simples doivent être nulles.

Critères d’usage :

- les tests d’expression doivent être lexicalement valides ;
- les phrases impossibles doivent tendre vers `0` ;
- les formulations lourdes doivent diminuer ;
- la morphologie explicite doit permettre un français simple plus naturel.

## Limites connues

Le projet reste volontairement contraint.

- ce n’est pas un dictionnaire complet du français ;
- certaines définitions restent plus fonctionnelles qu’élégantes ;
- la naturalité dépend encore d’une gestion explicite des formes dans `forms.txt` ;
- la fermeture lexicale impose parfois des reformulations moins idiomatiques qu’en français libre ;
- plusieurs mots très abstraits restent difficiles à définir sans un petit noyau quasi primitif.

Le corpus est donc très utile pour la cohérence, la pédagogie et la validation, mais il n’a pas vocation à remplacer l’usage libre de la langue.

## Usages possibles

- français contrôlé : pour produire un français limité, traçable et vérifiable ;
- dictionnaire définitoire : pour explorer un réseau de définitions lexicalement fermé ;
- langage simplifié : pour enseigner ou tester une expression simplifiée ;
- outil pédagogique : pour travailler les notions de définition, catégorie, reformulation et dépendance lexicale ;
- base pour validation automatique : pour détecter les mots hors vocabulaire, les définitions faibles ou les problèmes morphologiques ;
- corpus pour IA ou traitement automatique du langage : pour expérimenter un lexique contrôlé, un graphe définitoire, des tests de couverture ou des systèmes de génération contrainte.

## Référence actuelle

La branche de référence est la branche V6.2 stable :

- [wordlist_v6_2.txt](/Users/avialle/dev/minidico/wordlist_v6_2.txt)
- [dictionary_v6_2.json](/Users/avialle/dev/minidico/dictionary_v6_2.json)
- [forms_v6_2.txt](/Users/avialle/dev/minidico/forms_v6_2.txt)
- [README_V6_2.md](/Users/avialle/dev/minidico/README_V6_2.md)
- [validation_report_v6_2_final.md](/Users/avialle/dev/minidico/validation_report_v6_2_final.md)
- [expression_validation_conceptuelle_v6_2_final.md](/Users/avialle/dev/minidico/expression_validation_conceptuelle_v6_2_final.md)
