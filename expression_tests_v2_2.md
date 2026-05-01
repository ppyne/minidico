# Tests d expression V2.2

## politesse
### P1
- Phrase: `bonjour`
- Validation V2.1: `invalid`
- Mots absents en V2.1: bonjour
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: salutation minimale enfin disponible

### P2
- Phrase: `bonjour à vous`
- Validation V2.1: `invalid`
- Mots absents en V2.1: bonjour
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: salutation adressée

### P3
- Phrase: `merci`
- Validation V2.1: `invalid`
- Mots absents en V2.1: merci
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: remerciement minimal

### P4
- Phrase: `merci à vous`
- Validation V2.1: `invalid`
- Mots absents en V2.1: merci
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: remerciement adressé

### P5
- Phrase: `pardon`
- Validation V2.1: `invalid`
- Mots absents en V2.1: pardon
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: excuse minimale

### P6
- Phrase: `pardon, je ne comprendre pas`
- Validation V2.1: `invalid`
- Mots absents en V2.1: pardon
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: la réparation conversationnelle devient possible

### P7
- Phrase: `bonjour, je peux parler avec vous ?`
- Validation V2.1: `invalid`
- Mots absents en V2.1: bonjour
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: ouverture de contact simple

### P8
- Phrase: `merci pour votre travail`
- Validation V2.1: `invalid`
- Mots absents en V2.1: merci
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: remerciement pour une action

### P9
- Phrase: `pardon pour cette erreur`
- Validation V2.1: `invalid`
- Mots absents en V2.1: pardon
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: excuse explicite

### P10
- Phrase: `bonjour et merci`
- Validation V2.1: `invalid`
- Mots absents en V2.1: bonjour, merci
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: enchaînement très minimal mais habitable

## besoins corporels
### B1
- Phrase: `j’ai faim`
- Validation V2.1: `invalid`
- Mots absents en V2.1: faim
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: état corporel quotidien désormais direct

### B2
- Phrase: `j’ai soif`
- Validation V2.1: `invalid`
- Mots absents en V2.1: soif
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: état corporel quotidien désormais direct

### B3
- Phrase: `l’enfant a faim`
- Validation V2.1: `invalid`
- Mots absents en V2.1: faim
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: description simple de besoin

### B4
- Phrase: `la femme a soif`
- Validation V2.1: `invalid`
- Mots absents en V2.1: soif
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: description simple de besoin

### B5
- Phrase: `si j’ai faim, je manger`
- Validation V2.1: `invalid`
- Mots absents en V2.1: faim
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: la faim s exprime, mais la forme finie de manger manque encore

### B6
- Phrase: `si j’ai soif, je boire de l’eau`
- Validation V2.1: `invalid`
- Mots absents en V2.1: soif
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: la soif s exprime, mais la forme finie de boire manque encore

### B7
- Phrase: `vous avez faim ?`
- Validation V2.1: `invalid`
- Mots absents en V2.1: faim
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: question quotidienne simple

### B8
- Phrase: `vous avez soif ?`
- Validation V2.1: `invalid`
- Mots absents en V2.1: soif
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: question quotidienne simple

### B9
- Phrase: `nous avons faim et soif`
- Validation V2.1: `invalid`
- Mots absents en V2.1: faim, soif
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: coordination naturelle

### B10
- Phrase: `merci, je n’ai plus soif`
- Validation V2.1: `invalid`
- Mots absents en V2.1: merci, soif
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: bonne combinaison entre besoin et politesse

## orientation spatiale
### O1
- Phrase: `la porte est à gauche`
- Validation V2.1: `invalid`
- Mots absents en V2.1: gauche
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: orientation latérale élémentaire

### O2
- Phrase: `la fenêtre est à droite`
- Validation V2.1: `invalid`
- Mots absents en V2.1: droite
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: orientation latérale élémentaire

### O3
- Phrase: `il est devant la maison`
- Validation V2.1: `invalid`
- Mots absents en V2.1: devant
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: repère spatial courant

### O4
- Phrase: `elle est derrière la porte`
- Validation V2.1: `invalid`
- Mots absents en V2.1: derrière
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: repère spatial courant

### O5
- Phrase: `la voiture est devant`
- Validation V2.1: `invalid`
- Mots absents en V2.1: devant
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: compréhensible même sans complément

### O6
- Phrase: `le chat est derrière`
- Validation V2.1: `invalid`
- Mots absents en V2.1: derrière
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: compréhensible même sans complément

### O7
- Phrase: `allez à droite puis devant la maison`
- Validation V2.1: `invalid`
- Mots absents en V2.1: droite, devant
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: direction simple

### O8
- Phrase: `la place est à gauche de la route`
- Validation V2.1: `invalid`
- Mots absents en V2.1: gauche
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: description de lieu très utile

### O9
- Phrase: `reste devant`
- Validation V2.1: `invalid`
- Mots absents en V2.1: devant
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: acceptable
- Note: ordre bref mais naturel

### O10
- Phrase: `nous sommes derrière vous`
- Validation V2.1: `invalid`
- Mots absents en V2.1: derrière
- Validation V2.2 509: `ok`
- Validation V2.2 500: `ok`
- Diagnostic: naturel
- Note: bonne description relative

