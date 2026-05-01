# Diff V2.1 -> V2.2

## Ajouts pragmatiques

- `bonjour` : `mot pour parler à une personne au début de un jour`
- `merci` : `mot pour dire à une personne que on voir un bon effet de une action`
- `pardon` : `mot pour demander paix après une erreur ou un mal`
- `faim` : `besoin de manger`
- `soif` : `besoin de boire`
- `gauche` : `côté de une personne où le cœur est souvent plus près`
- `droite` : `côté de une personne où le cœur est souvent plus loin`
- `devant` : `place près de la face de une personne ou de une chose`
- `derrière` : `place loin de la face de une personne ou de une chose`

## Variante 509 mots

- Ajout simple des 9 mots pragmatiques sans perte de couverture existante.

## Variante 500 mots

- Pour rester à 500 mots, proposition de retirer: musique, fleur, herbe, arbre, outil, machine, train, genre, ressemblance.
- Ces 9 mots ont été choisis parce qu ils sont peu structurants, peu utilisés dans les tests d expression et non nécessaires aux définitions restantes.

## Effet sur les tests

- V2.1: 0/30
- V2.2 509: 30/30
- V2.2 500: 30/30
