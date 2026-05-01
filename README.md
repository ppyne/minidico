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

- [wordlist_v6_2.txt](/Users/avialle/dev/minidico/versions/v6_2/wordlist_v6_2.txt)
- [dictionary_v6_2.json](/Users/avialle/dev/minidico/versions/v6_2/dictionary_v6_2.json)
- [forms_v6_2.txt](/Users/avialle/dev/minidico/versions/v6_2/forms_v6_2.txt)
- [README_V6_2.md](/Users/avialle/dev/minidico/versions/v6_2/README_V6_2.md)
- [validation_report_v6_2_final.md](/Users/avialle/dev/minidico/versions/v6_2/validation_report_v6_2_final.md)
- [expression_validation_conceptuelle_v6_2_final.md](/Users/avialle/dev/minidico/versions/v6_2/expression_validation_conceptuelle_v6_2_final.md)

## Structure du dépôt

- `versions/v6_2/` : version stable de référence, avec la wordlist, le dictionnaire, les formes et les rapports finaux V6.2.
- `versions/stable/` : versions stables antérieures et historique lexical.
- `proposals/` : propositions intermédiaires, variantes checked et états pré-stabilisation.
- `docs/general/` : documentation transversale du projet.
- `docs/versions/` : README, changelogs et résumés des versions précédentes.
- `reports/` : validations, audits, diffs, métriques et rapports d’analyse.
- `tests/expression/` : batteries de phrases de test.
- `releases/` : paquet de publication V6.2 et archive ZIP.
- `src/check_dictionary.cpp` : validateur principal en C++.
- `Makefile` : compilation et exécution du validateur.

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

Le validateur travaille sur les noms attendus `wordlist.txt`, `dictionary.json` et `forms.txt`. Pour vérifier V6.2, il faut copier :

- `versions/v6_2/wordlist_v6_2.txt`
- `versions/v6_2/dictionary_v6_2.json`
- `versions/v6_2/forms_v6_2.txt`

dans un répertoire temporaire sous les noms `wordlist.txt`, `dictionary.json` et `forms.txt`, puis exécuter `./check_dictionary` depuis ce répertoire. La méthode complète est décrite dans [VALIDATION_METHOD.md](/Users/avialle/dev/minidico/docs/general/VALIDATION_METHOD.md).

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
