# Changelog V3

## V3.0 stable

Cette version fige la branche santé sur une base de 550 mots.

### Base de départ

- point de départ : branche V2.2 à 509 mots ;
- conservation de tout le vocabulaire V2.2 ;
- ajout de 41 mots orientés santé, biologie, reproduction, consentement et urgence.

### Fichiers stabilisés

- `wordlist_v3_0.txt`
- `dictionary_v3_0.json`
- `forms_v3_0.txt`

### Couverture ajoutée

- santé courante : `santé`, `fièvre`, `toux`, `fatigue`, `blessure`, `médicament`, `médecin`, `soin`, `guérir`, `urgence` ;
- corps et biologie : `organe`, `ventre`, `dos`, `gorge`, `poitrine`, `cerveau`, `muscle`, `cellule`, `respiration`, `respirer` ;
- fonctions corporelles : `uriner`, `saigner`, `vomir` ;
- reproduction et sexualité neutres : `sexe`, `sexuel`, `désir`, `plaisir`, `consentement`, `enceinte`, `grossesse`, `parent`, `père`, `mère`, `couple`, `protéger` ;
- système médical minimal : `hôpital`, `traitement`, `symptôme`, `maladie`, `danger`, `risque`.

### Résultats de validation

- 550 mots dans la liste ;
- 550 entrées dans le dictionnaire ;
- 0 mot hors vocabulaire dans les définitions ;
- 0 circularité directe simple ;
- 100 tests d’expression santé valides.

### Portée

V3.0 permet de parler de santé courante, de médecine simple, de biologie minimale du corps, de grossesse, de consentement et d’urgence de façon neutre et factuelle.

### Limites connues

- la médecine plus fine reste partielle ;
- plusieurs mots utiles pour une V3.1 sont encore absents : `infection`, `virus`, `allergie`, `opération`, `analyse`, `règles`, `préservatif` ;
- le système vise la clarté minimale, pas la précision clinique complète.
