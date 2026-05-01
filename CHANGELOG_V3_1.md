# Changelog V3.1

## V3.1 stable

Cette version fige la branche santé pratique sur une base de 600 mots.

### Base de départ

- point de départ : V3.0 stable à 550 mots ;
- conservation complète de la branche V3.0 ;
- ajout de 50 mots orientés infection, prévention, examens, pharmacie, anatomie plus fine et santé reproductive concrète.

### Fichiers stabilisés

- `wordlist_v3_1.txt`
- `dictionary_v3_1.json`
- `forms_v3_1.txt`

### Couverture ajoutée

- infection et prévention : `infection`, `virus`, `bactérie`, `allergie`, `vaccin`, `vacciner`, `prévention`, `prévenir`, `hygiène`, `contamination`, `contaminer` ;
- examens et parcours de soin : `examen`, `analyse`, `radio`, `test`, `consultation`, `patient`, `ordonnance`, `dose`, `pharmacie`, `clinique`, `infirmier`, `infirmière`, `opération` ;
- anatomie et biologie plus fines : `poumon`, `estomac`, `foie`, `rein`, `nerf` ;
- santé reproductive concrète : `utérus`, `vagin`, `pénis`, `sperme`, `ovule`, `règles`, `contraception`, `préservatif`, `sexualité`, `accoucher`, `ovaire`, `testicule`, `fertilité` ;
- urgence et suivi : `saignement`, `conscience`, `inconscient`, `positif`, `négatif`, `nausée`, `diarrhée`.

### Résultats de validation

- 600 mots dans la liste ;
- 600 entrées dans le dictionnaire ;
- 0 mot hors vocabulaire dans les définitions ;
- 0 circularité directe simple ;
- 100 tests d’expression santé valides.

### Portée

V3.1 étend V3.0 vers la santé pratique : infection, prévention, examens, pharmacie, santé reproductive concrète, urgence et conscience.

### Limites connues

- certaines notions cliniques fines restent absentes ;
- les accidents, mesures vitales et santé mentale détaillée demanderaient une V3.2 ;
- le système vise encore la clarté minimale plus que la précision médicale exhaustive.
