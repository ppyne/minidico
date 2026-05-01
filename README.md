# Dictionnaire français contrôlé minimal étendu

Ce projet construit un dictionnaire français à vocabulaire fermé, contrôlé et vérifiable automatiquement.
Il part d’une base minimale, puis l’étend par versions successives sans perdre la cohérence lexicale.
La version de référence actuelle est V6.2 stable.
Elle contient `1573` lemmes, `1573` entrées définitoires et `1227` formes reconnues.
Chaque définition doit rester à l’intérieur du vocabulaire autorisé ou des formes explicitement déclarées.
Le projet sert à définir, expliquer, comparer et raisonner dans un français contraint mais exploitable.
Il combine une liste de mots, un dictionnaire JSON, une table morphologique et un validateur C++.
Il produit aussi des rapports de validation stricte et des tests d’expression conceptuelle.
V6.2 conserve `0` mot hors vocabulaire, `0` circularité directe simple et `300/300` tests conceptuels valides.
Le dépôt est conçu à la fois comme ressource linguistique, outil pédagogique et base de validation automatique.

## Statut de V6.2

V6.2 est la version stable éditoriale et conceptuelle du projet.

- base : V6.0 stable ;
- extension : `12` concepts transversaux ajoutés ;
- nettoyage : accords suspects corrigés et formes orthographiques fautives ciblées supprimées ;
- validation stricte : `1573/1573` définitions conformes ;
- validation conceptuelle : `300/300` phrases valides, `0` impossible, `0` lourde.

Les fichiers de référence sont :

- [wordlist_v6_2.txt](/Users/avialle/dev/minidico/wordlist_v6_2.txt)
- [dictionary_v6_2.json](/Users/avialle/dev/minidico/dictionary_v6_2.json)
- [forms_v6_2.txt](/Users/avialle/dev/minidico/forms_v6_2.txt)
- [README_V6_2.md](/Users/avialle/dev/minidico/README_V6_2.md)
- [validation_report_v6_2_final.md](/Users/avialle/dev/minidico/validation_report_v6_2_final.md)
- [expression_validation_conceptuelle_v6_2_final.md](/Users/avialle/dev/minidico/expression_validation_conceptuelle_v6_2_final.md)

## Structure des fichiers

- `wordlist_v6_2.txt` : liste stable des lemmes autorisés.
- `dictionary_v6_2.json` : dictionnaire stable, une entrée par lemme.
- `forms_v6_2.txt` : table explicite `forme -> lemme` pour les pluriels, accords, conjugaisons et quelques formes éditoriales retenues.
- `src/check_dictionary.cpp` : validateur principal en C++.
- `Makefile` : compilation et exécution du validateur.
- `README_V6_2.md`, `CHANGELOG_V6_2.md`, `VERSION_SUMMARY_V6_2.md` : documentation de version.
- `PROJECT_OVERVIEW.md`, `TECHNICAL_ARCHITECTURE.md`, `VALIDATION_METHOD.md` : documentation générale.
- `validation_report_*.md`, `expression_validation_*.md`, `audit_*.md`, `diff_*.md` : rapports de contrôle et d’évolution.

## Comment valider

Compilation et exécution du validateur :

```sh
make
./check_dictionary
```

Ou directement :

```sh
make check
```

Le validateur travaille sur les noms attendus `wordlist.txt`, `dictionary.json` et `forms.txt`. Pour vérifier une version précise dans un répertoire temporaire, il faut y placer ces trois fichiers sous ces noms, puis exécuter `./check_dictionary` depuis ce répertoire. La méthode complète est décrite dans [VALIDATION_METHOD.md](/Users/avialle/dev/minidico/VALIDATION_METHOD.md).

## Exemple d’entrée JSON

Exemple simplifié d’entrée du dictionnaire :

```json
{
  "principe": {
    "categorie": "nom",
    "definition": "idée générale qui aide à comprendre, choisir, évaluer ou expliquer"
  }
}
```

Chaque entrée associe un lemme, une catégorie grammaticale et une définition rédigée dans le vocabulaire contrôlé.

## Limites connues

- ce n’est pas un dictionnaire complet du français ;
- la fermeture lexicale impose parfois des formulations moins idiomatiques que le français libre ;
- certaines définitions restent fonctionnelles avant d’être élégantes ;
- la qualité d’expression dépend encore d’une couche morphologique explicite dans `forms.txt` ;
- plusieurs notions très abstraites restent difficiles à définir sans un petit noyau quasi primitif.

## Licence

Ce projet est distribué sous licence `BSD-3-Clause`.
