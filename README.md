# Dictionnaire français minimal auto-cohérent

Ce dépôt contient une V0 concrète d'un dictionnaire français minimal à vocabulaire fermé.

## Contenu

- `wordlist.txt` : liste fermée de 500 mots.
- `dictionary.json` : 500 entrées alignées sur la liste.
- `forms.txt` : formes fléchies explicites pour la validation.
- `core_axioms.txt` : noyau limité de mots traités comme primitifs ou quasi primitifs.
- `src/check_dictionary.cpp` : validateur en C++17 sans dépendance externe.
- `missing_words.json` : rapport structuré des mots hors vocabulaire.
- `missing_words_report.md` : synthèse lisible des mots manquants.
- `validation_report.md` : bilan global de validation.
- `definition_graph.dot` : graphe lexical optionnel.
- `stats.json` : statistiques minimales.

## Choix de conception

Le projet suit la logique demandée dans la spécification :

- vocabulaire fermé ;
- V0 réelle avant raffinement ;
- définitions volontairement courtes ;
- quelques mots primitifs explicités ;
- vérification automatique reproductible.

Le choix du C++ est pragmatique :

- manipulation plus simple des chaînes et des ensembles ;
- parser JSON minimal embarqué ;
- aucune dépendance externe ;
- compilation directe avec un compilateur standard.

## Limites de la V0

Cette version cherche d'abord la cohérence formelle :

- toutes les entrées demandées existent ;
- la liste cible de 500 mots est atteinte ;
- les formes fléchies sont explicites ;
- les définitions restent parfois très pauvres sémantiquement.

Autrement dit, la V0 est faite pour stabiliser le système et l'outillage avant une V1 plus idiomatique.

## Utilisation

```sh
make
./check_dictionary
```

Ou directement :

```sh
make check
```

Les rapports sont régénérés à chaque exécution du validateur.

## Itérations recommandées

1. enrichir les définitions les plus centrales sans casser la fermeture lexicale ;
2. améliorer la détection des formes fléchies ;
3. ajouter un classement plus fin des dépendances lexicales ;
4. décider seulement ensuite si une extension à 750 mots est nécessaire.
