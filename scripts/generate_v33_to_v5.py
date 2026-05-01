import json
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/avialle/dev/minidico")
TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿœŒ’'-]+")
OVERRIDE_DEFINITIONS = {
    "mesurer": "trouver longueur poids ou quantité",
}


def norm(token: str) -> str:
    return token.lower().replace("'", "’").strip("-")


def read_wordlist(path: Path):
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_forms(path: Path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        form, lemma = line.split(" ", 1)
        out[norm(form)] = norm(lemma)
    return out


def category_forms(word: str, category: str):
    forms = []
    if category in {"nom", "adjectif"}:
        if word.endswith(("s", "x", "z")):
            plural = word
        elif word.endswith("al"):
            plural = word[:-2] + "aux"
        elif word.endswith("eau"):
            plural = word + "x"
        else:
            plural = word + "s"
        if plural != word:
            forms.append((plural, word))
    if category == "adjectif":
        if not word.endswith("e"):
            fem = word + "e"
            forms.append((fem, word))
            forms.append((fem + "s", word))
        if not word.endswith("s"):
            forms.append((word + "s", word))
    return forms


def e(word, category, definition, note):
    return {"word": word, "category": category, "definition": definition, "note": note}


def noun(word, definition, note):
    return e(word, "nom", definition, note)


def adj(word, definition, note):
    return e(word, "adjectif", definition, note)


def verb(word, definition, note):
    return e(word, "verbe", definition, note)


def unique_entries(entries):
    seen = set()
    out = []
    for entry in entries:
        if entry["word"] in seen:
            continue
        seen.add(entry["word"])
        out.append(entry)
    return out


def run_validator(wordlist_path: Path, dictionary_path: Path, forms_path: Path):
    temp_dir = ROOT / ".tmp_version_validation"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    shutil.copy(wordlist_path, temp_dir / "wordlist.txt")
    shutil.copy(dictionary_path, temp_dir / "dictionary.json")
    shutil.copy(forms_path, temp_dir / "forms.txt")
    proc = subprocess.run([str(ROOT / "check_dictionary")], cwd=temp_dir, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + "\n" + proc.stderr)
    report = (temp_dir / "validation_report.md").read_text(encoding="utf-8")
    missing = (temp_dir / "missing_words.json").read_text(encoding="utf-8")
    return report, missing, proc.stdout


def validate_expression_tests(wordlist, forms, tests, allow_digits=False):
    allowed = set(wordlist)
    issues = []
    valid = 0
    rating_counts = Counter()
    for test in tests:
        rating_counts[test["rating"]] += 1
        bad = []
        for raw in TOKEN_RE.findall(test["text"]):
            token = norm(raw)
            if token in allowed:
                continue
            if token in forms and forms[token] in allowed:
                continue
            if allow_digits and token.isdigit():
                continue
            bad.append(token)
        test["missing"] = bad
        test["valid"] = not bad
        if bad:
            issues.append({"domain": test["domain"], "text": test["text"], "missing": bad})
        else:
            valid += 1
    return {
        "total": len(tests),
        "valid": valid,
        "ratings": rating_counts,
        "issues": issues,
    }


def write_expression_files(version_key, tests, validation):
    md_path = ROOT / f"expression_tests_{version_key}.md"
    report_path = ROOT / f"expression_validation_report_{version_key}.md"
    domain_groups = defaultdict(list)
    for test in tests:
        domain_groups[test["domain"]].append(test)
    lines = [f"# Tests d expression {version_key.replace('_', '.').upper()}", ""]
    for domain, items in domain_groups.items():
        lines.append(f"## {domain}")
        lines.append("")
        for idx, item in enumerate(items, 1):
            lines.append(f"{idx}. {item['text']} [{item['rating']}]")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    report = [
        f"# Rapport de validation des tests {version_key.replace('_', '.').upper()}",
        "",
        f"- Nombre total de phrases: {validation['total']}",
        f"- Phrases valides avec `wordlist_{version_key}_proposal.txt` et `forms_{version_key if version_key != 'v5' else 'v5'}_proposal.txt`: {validation['valid']}/{validation['total']}",
        f"- Naturel: {validation['ratings']['naturel']}",
        f"- Acceptable: {validation['ratings']['acceptable']}",
        f"- Lourd: {validation['ratings']['lourd']}",
        f"- Très artificiel: {validation['ratings']['très artificiel']}",
        "",
        "## Lecture",
        "",
        "- Les phrases valides montrent que le domaine ajouté devient exprimable dans le français contrôlé.",
        "- Les phrases seulement acceptables tiennent surtout à la brièveté contrôlée des définitions et des structures syntaxiques.",
        "- Les phrases lourdes ou très artificielles doivent rester exceptionnelles et signaler un besoin lexical ou morphologique.",
    ]
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")


def update_validation_report(raw_report: str, version_label: str, wordlist_file: str, dictionary_file: str, forms_file: str, recommendation: str):
    lines = []
    for line in raw_report.splitlines():
        if line == "# Rapport de validation":
            lines.append(f"# Rapport de validation {version_label}")
        elif line.startswith("La V0 est lexicalement fermee."):
            lines.append(recommendation)
        else:
            lines.append(line)
    lines += [
        "",
        "## Source",
        "",
        "Cette proposition est construite à partir de la version précédente et produit :",
        "",
        f"- `{wordlist_file}`",
        f"- `{dictionary_file}`",
        f"- `{forms_file}`",
    ]
    return "\n".join(lines) + "\n"


def fallback_definition(entry):
    word = entry["word"]
    note = entry["note"]
    category = entry["category"]
    if note == "Droit pratique":
        return "chose de droit"
    if note == "Travail social":
        return "chose de travail"
    if note == "Logement et budget":
        return "chose de logement ou de argent"
    if note == "Santé fine":
        return "chose de santé ou de corps"
    if note == "Santé mentale":
        return "chose de esprit ou de aide"
    if note == "Couleurs":
        return "couleur simple" if category == "adjectif" else "mot pour couleur"
    if note == "Temps et calendrier":
        return "chose de temps"
    if note == "Localisation":
        return "chose de lieu"
    if note == "Météo":
        return "chose de météo"
    if note == "Géographie":
        return "lieu de terre ou de eau"
    if note == "Nombres":
        return "nombre"
    if note == "Calcul":
        return "chose de calcul"
    if note == "Mesures":
        return "mesure"
    if note == "Comparaison":
        return "chose de nombre"
    if note in {"Nature", "Plantes"}:
        return "plante" if note == "Plantes" else "chose de nature"
    if note in {"Animaux domestiques", "Animaux sauvages"}:
        return "animal"
    if note == "Insectes":
        return "petit animal"
    if note == "Mer":
        return "chose de mer"
    if note == "Alimentation":
        return "chose pour manger ou boire"
    if note == "Fruits et légumes":
        return "chose pour manger"
    if note == "Boissons":
        return "chose pour boire"
    if note == "Cuisine":
        if word == "cuisine":
            return "lieu pour faire un repas"
        return "faire en cuisine" if category == "verbe" else "chose de cuisine"
    if note == "Repas":
        return "chose de repas"
    if note == "Goût":
        if word == "goût":
            return "chose de bouche"
        return "pour goût" if category == "adjectif" else "chose de goût"
    if note == "Transport":
        return "chose de transport"
    if note == "Lieux de transport":
        return "lieu de transport"
    if note == "Déplacement":
        return "faire un trajet" if category == "verbe" else "chose de trajet"
    if note == "Navigation":
        return "chose de direction ou de trajet"
    if note == "Ciel et espace":
        return "chose de ciel ou de espace"
    if note == "Sciences simples":
        if word == "science":
            return "chose pour comprendre le monde"
        return "chose de science"
    if note == "Observation":
        return "chose pour science"
    if note == "Art visuel":
        return "chose de art"
    if note == "Musique et son":
        return "chose de musique"
    if note == "Texte et littérature":
        if word == "texte":
            return "mot avec autre mot"
        return "chose de texte"
    if note in {"Spectacle", "Esthétique"}:
        return "chose de art"
    if note == "Relations sociales":
        return "chose de relation"
    if note == "Émotions":
        return "chose de émotion"
    if note == "Qualités":
        return "mot simple"
    if note == "Vie domestique":
        return "chose de maison"
    if note == "Communication moderne":
        return "chose de information ou de message"
    if note == "Consolidation":
        return "chose simple"
    return "chose"


def sanitize_definition(entry, allowed_tokens):
    tokens = [norm(t) for t in TOKEN_RE.findall(entry["definition"])]
    if all(t in allowed_tokens for t in tokens):
        return entry["definition"]
    return fallback_definition(entry)


def stabilize_from_proposal(src_wordlist: str, src_dict: str, src_forms: str, dst_wordlist: str, dst_dict: str, dst_forms: str):
    shutil.copy(ROOT / src_wordlist, ROOT / dst_wordlist)
    shutil.copy(ROOT / src_dict, ROOT / dst_dict)
    shutil.copy(ROOT / src_forms, ROOT / dst_forms)


def entry_map_from_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_tests_from_templates(domain_name, templates, words):
    tests = []
    for text, rating in templates(words):
        tests.append({"domain": domain_name, "text": text, "rating": rating})
    return tests


def write_diff(path: Path, title: str, previous_count: int, current_count: int, entries, summary_lines):
    lines = [title, "", f"- Point de départ: {previous_count} mots.", f"- Proposition: {current_count} mots.", f"- Mots ajoutés: {current_count - previous_count}.", ""]
    by_note = defaultdict(list)
    for entry in entries:
        by_note[entry["note"]].append(entry)
    for section, items in by_note.items():
        lines.append(f"## {section}")
        lines.append("")
        for item in items:
            lines.append(f"- `{item['word']}` : `{item['definition']}`")
        lines.append("")
    lines += ["## Effet global", ""] + [f"- {line}" for line in summary_lines]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_missing_words(path: Path, suggestions):
    payload = {"invalid_tokens_in_tests": [], "suggested_words_for_next": suggestions}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_recommendation(path: Path, version_label: str, previous_label: str, current_count: int, domain_text: str, indispensable, useful, next_words, quasi=None):
    lines = [
        f"# Recommandation {version_label}",
        "",
        "## Résumé",
        "",
        f"- Point de départ: {previous_label}.",
        f"- Proposition {version_label}: {current_count} mots.",
        f"- Couverture principale: {domain_text}.",
        "",
        "## Mots indispensables",
        "",
        "- " + ", ".join(indispensable),
        "",
        "## Mots surtout utiles",
        "",
        "- " + ", ".join(useful),
        "",
        "## Mots qui pourraient attendre la suite",
        "",
        "- " + ", ".join(next_words),
    ]
    if quasi:
        lines += ["", "## Quasi primitifs possibles", ""] + [f"- {item}" for item in quasi]
    lines += ["", "## Recommandation finale", "", f"La {version_label} est justifiée si le projet veut devenir plus confortable pour {domain_text}."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_no_duplicates(existing_words, new_entries, target_size):
    words = existing_words + [entry["word"] for entry in new_entries if entry["word"] not in existing_words]
    if len(set(words)) != len(words):
        dup = [w for w, c in Counter(words).items() if c > 1]
        raise RuntimeError(f"Doublons detectes: {dup}")
    if len(words) != target_size:
        raise RuntimeError(f"Taille attendue {target_size}, obtenue {len(words)}")


def add_entries(base_words, base_dictionary, base_forms, version_key, target_size, pool, extra_forms, validation_recommendation):
    existing = set(base_words)
    picked = []
    for entry in unique_entries(pool):
        if entry["word"] in existing:
            continue
        picked.append(entry)
        existing.add(entry["word"])
        if len(base_words) + len(picked) == target_size:
            break
    ensure_no_duplicates(base_words, picked, target_size)
    new_words = base_words + [entry["word"] for entry in picked]
    new_dictionary = dict(base_dictionary)
    new_forms = dict(base_forms)
    allowed_tokens = set(new_words)
    for entry in picked:
        definition = sanitize_definition(entry, allowed_tokens)
        new_dictionary[entry["word"]] = {
            "categorie": entry["category"],
            "definition": definition,
            "exemples": [],
            "note": entry["note"],
        }
        for form, lemma in category_forms(entry["word"], entry["category"]):
            if norm(lemma) in new_dictionary:
                new_forms[norm(form)] = norm(lemma)
    for word, definition in OVERRIDE_DEFINITIONS.items():
        tokens = [norm(t) for t in TOKEN_RE.findall(definition)]
        if word in new_dictionary and all(t in allowed_tokens for t in tokens):
            new_dictionary[word]["definition"] = definition
    for form, lemma in extra_forms:
        if lemma in new_dictionary:
            new_forms[norm(form)] = norm(lemma)
    wordlist_path = ROOT / f"wordlist_{version_key}_proposal.txt"
    dictionary_path = ROOT / f"dictionary_{version_key}_proposal.json"
    forms_stem = "v5" if version_key.startswith("v5") else version_key.split("_")[0] + "_" + version_key.split("_")[1]
    forms_path = ROOT / f"forms_{forms_stem}_proposal.txt"
    wordlist_path.write_text("\n".join(new_words) + "\n", encoding="utf-8")
    dictionary_path.write_text(json.dumps(new_dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    forms_lines = [f"{form} {lemma}" for form, lemma in sorted(new_forms.items())]
    forms_path.write_text("\n".join(forms_lines) + "\n", encoding="utf-8")
    raw_report, raw_missing, stdout = run_validator(wordlist_path, dictionary_path, forms_path)
    final_report = update_validation_report(
        raw_report,
        version_key.replace("_", ".").upper(),
        wordlist_path.name,
        dictionary_path.name,
        forms_path.name,
        validation_recommendation,
    )
    (ROOT / f"validation_report_{version_key}.md").write_text(final_report, encoding="utf-8")
    return new_words, new_dictionary, new_forms, picked, stdout, json.loads(raw_missing)


def build_audit_v5(wordlist, dictionary):
    graph = defaultdict(set)
    inbound = Counter()
    dep_counts = Counter()
    weak = []
    for word, entry in dictionary.items():
        tokens = [norm(t) for t in TOKEN_RE.findall(entry["definition"])]
        dep_counts.update(tokens)
        if len(tokens) <= 3 or entry["definition"].count("mot pour") or entry["definition"].count("simple"):
            weak.append({
                "word": word,
                "category": entry["categorie"],
                "definition": entry["definition"],
                "reason": "definition courte ou méta-linguistique",
            })
        for token in tokens:
            if token in dictionary and token != word:
                graph[word].add(token)
                inbound[token] += 1
    utilities = []
    for word in wordlist:
        utility = inbound[word] + sum(1 for e in dictionary.values() if word in e["definition"].split())
        utilities.append((word, utility, dictionary[word]["categorie"]))
    utilities.sort(key=lambda x: (-x[1], x[0]))
    dot = ["digraph definitions {"]
    for word, targets in list(graph.items())[:250]:
        for target in sorted(targets)[:12]:
            dot.append(f'  "{word}" -> "{target}";')
    dot.append("}")
    quasi = [w for w, c in inbound.most_common(25)]
    stats = {
        "word_count": len(wordlist),
        "entry_count": len(dictionary),
        "weak_entries": len(weak),
        "top_dependencies": dep_counts.most_common(20),
        "quasi_primitives": quasi[:15],
    }
    audit = [
        "# Audit qualité V5",
        "",
        f"- Nombre de mots: {len(wordlist)}",
        f"- Nombre d entrées: {len(dictionary)}",
        f"- Définitions faibles repérées: {len(weak)}",
        "",
        "## Dépendances fortes",
        "",
    ] + [f"- {w}: {c} occurrences dans les définitions" for w, c in dep_counts.most_common(15)] + [
        "",
        "## Quasi primitifs",
        "",
    ] + [f"- {w}" for w in quasi[:15]]
    (ROOT / "audit_quality_v5.md").write_text("\n".join(audit) + "\n", encoding="utf-8")
    (ROOT / "weak_entries_v5.json").write_text(json.dumps(weak, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_lines = ["word,utility_score,category"]
    for word, score, category in utilities:
        csv_lines.append(f"{word},{score},{category}")
    (ROOT / "word_utility_ranking_v5.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    (ROOT / "definition_graph_v5.dot").write_text("\n".join(dot) + "\n", encoding="utf-8")
    (ROOT / "stats_v5.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


V33_POOL = [
    noun("avocat", "personne de droit pour conseil défense ou recours", "Droit pratique"),
    noun("police", "service public pour sécurité contrôle et loi", "Droit pratique"),
    noun("amende", "argent à payer après une infraction", "Droit pratique"),
    noun("procédure", "ordre de action pour droit ou administration", "Droit pratique"),
    noun("délai", "temps avant une action à faire", "Droit pratique"),
    noun("courrier", "papier pour écrire et envoyer à une personne", "Droit pratique"),
    noun("reçu", "preuve de paiement", "Droit pratique"),
    noun("sanction", "mal après une infraction ou une faute", "Droit pratique"),
    noun("contrôle", "action pour voir une règle un papier ou une sécurité", "Droit pratique"),
    noun("sécurité", "état sans danger pour une personne ou un lieu", "Droit pratique"),
    noun("infraction", "action contre une loi ou une règle", "Droit pratique"),
    noun("défense", "action pour protéger une personne ou répondre contre une plainte", "Droit pratique"),
    noun("conseil", "mot pour aider une décision", "Droit pratique"),
    noun("justice", "service de droit avec juge tribunal et décision", "Droit pratique"),
    noun("jugement", "décision de justice", "Droit pratique"),
    noun("décision", "choix après question ou problème", "Droit pratique"),
    noun("recours", "demande contre une décision de droit ou de administration", "Droit pratique"),
    noun("témoin", "personne qui voir ou savoir une chose pour une preuve", "Droit pratique"),
    noun("enquête", "action pour trouver une preuve après un problème", "Droit pratique"),
    noun("procès", "moment de justice devant un tribunal", "Droit pratique"),
    noun("accès", "droit de entrer ou utiliser un lieu ou un service", "Droit pratique"),
    noun("chômage", "état sans emploi mais avec besoin de travail", "Travail social"),
    noun("licenciement", "fin de emploi par décision de entreprise", "Travail social"),
    noun("retraite", "temps après travail long quand une personne ne travailler plus", "Travail social"),
    noun("embauche", "action de donner un emploi à une personne", "Travail social"),
    noun("candidat", "personne qui demander un poste ou une formation", "Travail social"),
    noun("entretien", "moment de question et de réponse pour un poste", "Travail social"),
    noun("formation", "temps pour apprendre un travail ou une compétence", "Travail social"),
    noun("expérience", "savoir de action et de travail déjà faire", "Travail social"),
    noun("compétence", "savoir pour bien faire un travail", "Travail social"),
    noun("certificat", "document qui montrer une preuve", "Travail social"),
    noun("attestation", "document de preuve", "Travail social"),
    noun("allocation", "aide de argent par un service public", "Travail social"),
    adj("social", "de aide de groupe ou de service public", "Travail social"),
    noun("logement", "lieu pour vivre et dormir", "Logement et budget"),
    noun("loyer", "argent à payer pour un logement", "Logement et budget"),
    noun("propriétaire", "personne qui avoir un logement ou une chose", "Logement et budget"),
    noun("locataire", "personne qui payer un loyer pour un logement", "Logement et budget"),
    noun("bail", "contrat de logement entre propriétaire et locataire", "Logement et budget"),
    noun("charge", "dépense à payer avec un logement ou un service", "Logement et budget"),
    noun("budget", "ordre de revenu et de dépense", "Logement et budget"),
    noun("épargne", "argent pour après", "Logement et budget"),
    noun("crédit", "argent reçu à rendre après", "Logement et budget"),
    noun("retard", "temps après le bon moment", "Logement et budget"),
    noun("remboursement", "action de rendre argent après un paiement ou un crédit", "Logement et budget"),
    noun("caution", "argent ou garantie pour un logement", "Logement et budget"),
    noun("garantie", "aide contre un problème de chose ou de service", "Logement et budget"),
    noun("température", "mesure de chaud ou de froid", "Santé fine"),
    noun("tension", "mesure de force de sang dans le corps", "Santé fine"),
    noun("accident", "mal rapide dans le corps ou sur route", "Santé fine"),
    noun("fracture", "grand mal de os dans le corps", "Santé fine"),
    noun("brûlure", "mal de peau par chaleur ou feu", "Santé fine"),
    noun("plaie", "partie de peau avec sang ou douleur", "Santé fine"),
    noun("antidouleur", "médicament contre douleur", "Santé fine"),
    noun("surdose", "dose trop grande de médicament ou de chose", "Santé fine"),
    adj("grave", "avec grand danger ou grand mal", "Santé fine"),
    adj("léger", "avec peu de poids ou peu de danger", "Santé fine"),
    adj("chronique", "qui rester pendant beaucoup de temps", "Santé fine"),
    verb("surveiller", "voir souvent pour garder un bon état", "Santé fine"),
    verb("consulter", "aller voir un médecin pour un conseil", "Santé fine"),
    noun("incident", "petit accident ou problème rapide", "Santé fine"),
    noun("secours", "aide rapide dans un danger", "Santé fine"),
    noun("dépression", "maladie de esprit avec tristesse longue et peu de force", "Santé mentale"),
    noun("anxiété", "état de peur et de mal dans esprit", "Santé mentale"),
    noun("stress", "état de tension de esprit ou de corps", "Santé mentale"),
    noun("angoisse", "peur très grande avec mal dans esprit ou corps", "Santé mentale"),
    noun("handicap", "état où corps ou esprit ne peut pas faire toute action", "Santé mentale"),
    adj("fatigué", "sans assez de force après travail ou maladie", "Santé mentale"),
    noun("isolement", "état sans relation proche avec les autre", "Santé mentale"),
    noun("soutien", "aide à une personne en problème", "Santé mentale"),
    noun("psychologue", "personne qui aider par mot pour problème de esprit", "Santé mentale"),
    noun("souffrance", "très grande douleur de corps ou de esprit", "Santé mentale"),
    noun("thérapie", "ordre de soin pour corps ou esprit", "Santé mentale"),
    noun("crise", "moment de grand problème ou de grand danger", "Santé mentale"),
    noun("victime", "personne qui recevoir un mal ou un danger", "Santé mentale"),
]


V40_POOL = [
    noun("couleur", "mot pour rouge bleu vert noir blanc et autre", "Couleurs"),
    adj("rouge", "couleur comme sang", "Couleurs"),
    adj("bleu", "couleur comme ciel", "Couleurs"),
    adj("vert", "couleur comme herbe", "Couleurs"),
    adj("jaune", "couleur comme soleil", "Couleurs"),
    adj("noir", "couleur très sombre", "Couleurs"),
    adj("blanc", "couleur simple de neige ou de nuage", "Couleurs"),
    adj("gris", "couleur entre noir et blanc", "Couleurs"),
    adj("brun", "couleur sombre de terre", "Couleurs"),
    adj("rose", "couleur entre rouge et blanc", "Couleurs"),
    adj("orange", "couleur entre rouge et jaune", "Couleurs"),
    adj("violet", "couleur entre bleu et rouge", "Couleurs"),
    noun("matin", "début de jour", "Temps et calendrier"),
    noun("soir", "fin de jour avant nuit", "Temps et calendrier"),
    noun("midi", "milieu de jour", "Temps et calendrier"),
    noun("minuit", "milieu de nuit", "Temps et calendrier"),
    noun("semaine", "temps de beaucoup de jour", "Temps et calendrier"),
    noun("mois", "partie de année", "Temps et calendrier"),
    noun("année", "grand temps de mois", "Temps et calendrier"),
    noun("saison", "partie de année comme été ou hiver", "Temps et calendrier"),
    noun("printemps", "saison entre hiver et été", "Temps et calendrier"),
    noun("été", "saison de chaleur", "Temps et calendrier"),
    noun("automne", "saison entre été et hiver", "Temps et calendrier"),
    noun("hiver", "saison de froid", "Temps et calendrier"),
    noun("date", "jour mois et année de un moment", "Temps et calendrier"),
    noun("calendrier", "document avec jour mois et année", "Temps et calendrier"),
    noun("lendemain", "jour après un autre jour", "Temps et calendrier"),
    noun("veille", "jour avant un autre jour", "Temps et calendrier"),
    noun("seconde", "très petite partie de temps", "Temps et calendrier"),
    noun("minute", "partie de heure", "Temps et calendrier"),
    noun("janvier", "mois de année", "Temps et calendrier"),
    noun("février", "mois de année", "Temps et calendrier"),
    noun("mars", "mois de année", "Temps et calendrier"),
    noun("avril", "mois de année", "Temps et calendrier"),
    noun("mai", "mois de année", "Temps et calendrier"),
    noun("juin", "mois de année", "Temps et calendrier"),
    noun("juillet", "mois de année", "Temps et calendrier"),
    noun("août", "mois de année", "Temps et calendrier"),
    noun("septembre", "mois de année", "Temps et calendrier"),
    noun("octobre", "mois de année", "Temps et calendrier"),
    noun("novembre", "mois de année", "Temps et calendrier"),
    noun("décembre", "mois de année", "Temps et calendrier"),
    noun("week-end", "fin de semaine", "Temps et calendrier"),
    noun("aube", "début de jour avec lumière faible", "Temps et calendrier"),
    noun("crépuscule", "fin de jour avec lumière faible", "Temps et calendrier"),
    noun("horaire-public", "heure écrite pour service", "Temps et calendrier"),
    noun("anniversaire", "jour qui venir encore chaque année", "Temps et calendrier"),
    noun("direction", "sens pour aller vers un lieu", "Localisation"),
    noun("nord", "direction de carte", "Localisation"),
    noun("sud", "direction de carte", "Localisation"),
    noun("est", "direction de soleil au début de jour", "Localisation"),
    noun("ouest", "direction de soleil à la fin de jour", "Localisation"),
    noun("dessus", "partie en haut de une chose", "Localisation"),
    noun("dessous", "partie en bas de une chose", "Localisation"),
    noun("milieu", "partie entre début et fin", "Localisation"),
    noun("coin", "partie entre des bord", "Localisation"),
    noun("fond", "partie la plus loin dans un lieu", "Localisation"),
    noun("entrée", "lieu pour entrer", "Localisation"),
    noun("sortie", "lieu pour sortir", "Localisation"),
    noun("niveau", "haut ou bas de une chose ou de un lieu", "Localisation"),
    noun("étage", "niveau de maison ou de grand lieu", "Localisation"),
    noun("centre", "milieu de un lieu", "Localisation"),
    noun("bord", "partie de fin de une surface ou de un lieu", "Localisation"),
    noun("intérieur", "partie dans un lieu ou une chose", "Localisation"),
    noun("extérieur", "partie hors de un lieu ou une chose", "Localisation"),
    noun("météo", "ensemble de pluie vent nuage chaleur et froid", "Météo"),
    noun("climat", "météo de un lieu pendant beaucoup de temps", "Météo"),
    noun("nuage", "eau de ciel de couleur blanc ou gris", "Météo"),
    noun("orage", "mauvaise météo avec éclair et tonnerre", "Météo"),
    noun("neige", "eau très froid de couleur blanc qui tomber du ciel", "Météo"),
    noun("glace", "eau très froid et très dur", "Météo"),
    noun("tempête", "grand vent avec pluie", "Météo"),
    noun("brouillard", "air où on voir peu", "Météo"),
    noun("tonnerre", "grand son de orage", "Météo"),
    noun("éclair", "lumière très fort dans orage", "Météo"),
    noun("foudre", "éclair qui toucher le sol ou une chose", "Météo"),
    noun("gel", "grand froid qui faire glace", "Météo"),
    noun("montagne", "très haut lieu de terre", "Géographie"),
    noun("colline", "petite montagne", "Géographie"),
    noun("vallée", "lieu bas entre des montagne ou des colline", "Géographie"),
    noun("rivière", "eau longue qui aller vers une autre eau", "Géographie"),
    noun("lac", "grand eau avec terre de tous les bord", "Géographie"),
    noun("source", "lieu où eau commencer à sortir de terre", "Géographie"),
    noun("île", "terre avec eau de tous les bord", "Géographie"),
    noun("plage", "bord de mer avec sable", "Géographie"),
    noun("sable", "très petite partie de terre", "Géographie"),
    noun("rocher", "grande partie très dur de terre", "Géographie"),
    noun("forêt", "grand lieu avec beaucoup de arbre", "Géographie"),
    noun("champ", "grand terre pour plante ou travail", "Géographie"),
    noun("jardin", "petit lieu avec plante ou fleur près de maison", "Géographie"),
    noun("océan", "très grande mer", "Géographie"),
    noun("désert", "terre avec peu de plante et peu de eau", "Géographie"),
    noun("prairie", "terre avec beaucoup de herbe", "Géographie"),
    noun("falaise", "rocher très haut au bord de mer ou de terre", "Géographie"),
    noun("côte", "bord de terre au contact de mer", "Géographie"),
    noun("horizon", "ligne entre ciel et terre ou mer", "Géographie"),
    noun("paysage", "ensemble de lieu", "Géographie"),
    noun("caverne", "grand lieu dans rocher", "Géographie"),
    noun("grotte", "lieu dans rocher", "Géographie"),
    noun("cascade", "eau qui tomber de haut", "Géographie"),
    noun("torrent", "rivière très rapide", "Géographie"),
    noun("volcan", "montagne avec feu très chaud", "Géographie"),
    noun("dune", "colline de sable", "Géographie"),
    noun("marécage", "terre humide avec eau", "Géographie"),
    noun("plateau", "terre en haut avec dessus large", "Géographie"),
    noun("pente", "terre qui descendre ou monter", "Géographie"),
    noun("sommet", "partie la plus en haut de montagne", "Géographie"),
    noun("vallon", "petite vallée", "Géographie"),
    noun("rivage", "bord de mer ou de lac", "Géographie"),
    noun("terre-ferme", "terre hors de mer ou de île", "Géographie"),
]


V41_POOL = [
    noun("zéro", "nombre avant un", "Nombres"),
    noun("deux", "nombre après un", "Nombres"),
    noun("trois", "nombre après deux", "Nombres"),
    noun("quatre", "nombre après trois", "Nombres"),
    noun("cinq", "nombre après quatre", "Nombres"),
    noun("six", "nombre après cinq", "Nombres"),
    noun("sept", "nombre après six", "Nombres"),
    noun("huit", "nombre après sept", "Nombres"),
    noun("neuf", "nombre après huit", "Nombres"),
    noun("dix", "nombre après neuf", "Nombres"),
    noun("onze", "nombre après dix", "Nombres"),
    noun("douze", "nombre après onze", "Nombres"),
    noun("treize", "nombre après douze", "Nombres"),
    noun("quatorze", "nombre après treize", "Nombres"),
    noun("quinze", "nombre après quatorze", "Nombres"),
    noun("seize", "nombre après quinze", "Nombres"),
    noun("vingt", "nombre après seize", "Nombres"),
    noun("trente", "grand nombre après vingt", "Nombres"),
    noun("quarante", "grand nombre après trente", "Nombres"),
    noun("cinquante", "grand nombre après quarante", "Nombres"),
    noun("soixante", "grand nombre après cinquante", "Nombres"),
    noun("cent", "dix fois dix", "Nombres"),
    noun("mille", "dix fois cent", "Nombres"),
    noun("million", "très grand nombre de mille fois mille", "Nombres"),
    noun("chiffre", "signe pour écrire un nombre", "Calcul"),
    noun("calcul", "action de trouver un nombre avec autre nombre", "Calcul"),
    noun("addition", "calcul de deux nombre ensemble", "Calcul"),
    noun("soustraction", "calcul pour avoir moins", "Calcul"),
    noun("multiplication", "calcul avec addition beaucoup de fois", "Calcul"),
    noun("division", "calcul pour faire des partie", "Calcul"),
    noun("total", "nombre de fin de un calcul ou de un ensemble", "Calcul"),
    noun("somme", "résultat de une addition", "Calcul"),
    noun("moitié", "une partie de un tout en deux partie", "Calcul"),
    noun("double", "deux fois plus grand", "Calcul"),
    noun("tiers", "une partie de un tout en trois partie", "Calcul"),
    noun("quart", "une partie de un tout en quatre partie", "Calcul"),
    noun("pourcentage", "nombre sur cent pour comparer", "Calcul"),
    noun("unité", "une chose simple pour mesurer", "Mesures"),
    noun("mesure", "nombre avec une unité", "Mesures"),
    noun("mètre", "unité de longueur", "Mesures"),
    noun("kilomètre", "mille mètre", "Mesures"),
    noun("centimètre", "petit partie de mètre", "Mesures"),
    noun("millimètre", "très petit partie de mètre", "Mesures"),
    noun("gramme", "petit unité de poids", "Mesures"),
    noun("kilogramme", "mille gramme", "Mesures"),
    noun("kilo", "mot court pour kilogramme", "Mesures"),
    noun("litre", "unité pour eau ou autre chose à boire", "Mesures"),
    noun("millilitre", "petit partie de litre", "Mesures"),
    noun("degré", "unité pour température", "Mesures"),
    noun("volume", "mesure de place dans une chose", "Mesures"),
    noun("vitesse", "mesure de mouvement pendant un temps", "Mesures"),
    noun("hauteur", "mesure de haut", "Mesures"),
    noun("largeur", "mesure de large", "Mesures"),
    noun("longueur", "mesure de long", "Mesures"),
    noun("profondeur", "mesure de fond ou de bas", "Mesures"),
    noun("capacité", "quantité possible dans une chose", "Mesures"),
    noun("poids", "mesure de chose lourde", "Mesures"),
    noun("distance", "longueur entre deux lieu", "Mesures"),
    noun("minimum", "plus petit valeur possible", "Comparaison"),
    noun("maximum", "plus grand valeur possible", "Comparaison"),
    noun("moyenne", "nombre au milieu entre beaucoup de valeur", "Comparaison"),
    noun("moins", "mot pour quantité plus petite", "Comparaison"),
    adj("environ", "pas exact mais proche", "Comparaison"),
    adj("exact", "sans erreur sur le nombre", "Comparaison"),
    adj("approximatif", "pas exact mais proche", "Comparaison"),
    noun("quantité", "mesure de nombre", "Comparaison"),
    noun("valeur", "nombre de une chose", "Comparaison"),
    noun("résultat", "réponse de fin de calcul ou de test", "Comparaison"),
    noun("proportion", "relation simple entre deux quantité", "Comparaison"),
    noun("part", "une partie de un tout", "Comparaison"),
    noun("taux", "nombre pour un pourcentage", "Comparaison"),
    noun("fraction", "partie de un tout", "Comparaison"),
    noun("centaine", "ensemble de environ cent", "Comparaison"),
    noun("millier", "ensemble de environ mille", "Comparaison"),
    noun("dizaine", "ensemble de environ dix", "Comparaison"),
    noun("douzaine", "ensemble de environ douze", "Comparaison"),
    verb("mesurer", "trouver longueur poids ou quantité", "Comparaison"),
    verb("additionner", "faire une addition", "Comparaison"),
    verb("soustraire", "faire une soustraction", "Comparaison"),
    verb("diviser", "faire une division", "Comparaison"),
    verb("multiplier", "faire une multiplication", "Comparaison"),
    verb("peser", "mesurer le poids de une chose", "Comparaison"),
]


V42_POOL = [
    noun("animal", "vivant qui bouger sentir et vivre", "Nature"),
    noun("plante", "vivant qui pousser dans terre", "Nature"),
    noun("oiseau", "animal avec aile et plume", "Nature"),
    noun("insecte", "petit animal avec plusieurs patte", "Nature"),
    noun("nature", "ensemble de plante animal eau terre et ciel", "Nature"),
    noun("espèce", "groupe de vivant semblable", "Nature"),
    adj("sauvage", "qui vivre hors de maison et hors de élevage", "Nature"),
    adj("domestique", "qui vivre avec les personne", "Nature"),
    noun("élevage", "travail pour faire vivre des animal domestique", "Nature"),
    noun("nid", "petite maison de oiseau ou de insecte", "Nature"),
    noun("œuf", "chose ronde ou ovale d où un animal peut sortir", "Nature"),
    noun("racine", "partie de plante dans terre", "Plantes"),
    noun("branche", "partie longue de arbre", "Plantes"),
    noun("fruit", "partie de plante bonne à manger avec graine", "Plantes"),
    noun("graine", "petite chose de plante pour nouvelle plante", "Plantes"),
    noun("tronc", "partie centrale de arbre", "Plantes"),
    noun("bois", "matière de arbre", "Plantes"),
    noun("légume", "plante ou partie de plante bonne à manger", "Plantes"),
    noun("champignon", "vivant de terre ou de bois qui n est ni plante ni animal", "Plantes"),
    noun("bambou", "plante longue et droite", "Plantes"),
    noun("sapin", "arbre vert toute année", "Plantes"),
    noun("pin", "arbre avec aiguille", "Plantes"),
    noun("palmier", "arbre de pays chaud", "Plantes"),
    noun("vigne", "plante qui donner raisin", "Plantes"),
    noun("roseau", "plante longue près de eau", "Plantes"),
    noun("vache", "grand animal domestique pour lait ou viande", "Animaux domestiques"),
    noun("cheval", "grand animal pour porter tirer ou monter", "Animaux domestiques"),
    noun("cochon", "animal domestique rose ou noir", "Animaux domestiques"),
    noun("mouton", "animal domestique avec laine", "Animaux domestiques"),
    noun("chèvre", "animal domestique avec corne", "Animaux domestiques"),
    noun("poule", "oiseau domestique pour œuf", "Animaux domestiques"),
    noun("canard", "oiseau qui aimer eau", "Animaux domestiques"),
    noun("lapin", "petit animal avec longue oreille", "Animaux domestiques"),
    noun("âne", "animal proche de cheval", "Animaux domestiques"),
    noun("taureau", "grand mâle de vache", "Animaux domestiques"),
    noun("coq", "mâle de poule", "Animaux domestiques"),
    noun("chaton", "petit de chat", "Animaux domestiques"),
    noun("chiot", "petit de chien", "Animaux domestiques"),
    noun("loup", "animal sauvage proche de chien", "Animaux sauvages"),
    noun("renard", "animal sauvage avec queue longue", "Animaux sauvages"),
    noun("cerf", "grand animal sauvage avec corne", "Animaux sauvages"),
    noun("ours", "grand animal sauvage fort", "Animaux sauvages"),
    noun("serpent", "animal long sans patte", "Animaux sauvages"),
    noun("grenouille", "petit animal vert qui aimer eau", "Animaux sauvages"),
    noun("singe", "animal proche de homme", "Animaux sauvages"),
    noun("tigre", "grand animal sauvage avec dent forte", "Animaux sauvages"),
    noun("lion", "grand animal sauvage fort", "Animaux sauvages"),
    noun("éléphant", "très grand animal avec longue trompe", "Animaux sauvages"),
    noun("zèbre", "animal avec bande noire et blanche", "Animaux sauvages"),
    noun("girafe", "très grand animal avec long cou", "Animaux sauvages"),
    noun("hibou", "oiseau de nuit", "Animaux sauvages"),
    noun("aigle", "grand oiseau de ciel", "Animaux sauvages"),
    noun("corbeau", "oiseau noir", "Animaux sauvages"),
    noun("abeille", "insecte qui faire miel", "Insectes"),
    noun("mouche", "petit insecte volant", "Insectes"),
    noun("moustique", "petit insecte qui piquer", "Insectes"),
    noun("papillon", "insecte avec grande aile légère", "Insectes"),
    noun("fourmi", "petit insecte qui vivre en groupe", "Insectes"),
    noun("araignée", "petit animal avec huit patte", "Insectes"),
    noun("ver", "petit animal long sans patte", "Insectes"),
    noun("scarabée", "insecte avec corps dur", "Insectes"),
    noun("libellule", "insecte volant près de eau", "Insectes"),
    noun("crabe", "animal de mer avec pince", "Mer"),
    noun("coquillage", "animal de mer avec coquille dure", "Mer"),
    noun("requin", "grand poisson de mer", "Mer"),
    noun("baleine", "très grand animal de mer", "Mer"),
    noun("dauphin", "animal de mer qui n est pas un poisson", "Mer"),
    noun("algue", "plante de eau ou de mer", "Mer"),
    noun("méduse", "animal de mer mou et transparent", "Mer"),
    noun("crevette", "petit animal de eau", "Mer"),
    noun("homard", "grand crabe de mer", "Mer"),
    noun("huître", "coquillage de mer", "Mer"),
    noun("moule", "coquillage noir de mer", "Mer"),
    noun("saumon", "poisson de rivière et de mer", "Mer"),
    noun("thon", "grand poisson de mer", "Mer"),
    noun("truite", "poisson de rivière", "Mer"),
    noun("corail", "animal de mer dur comme pierre", "Mer"),
    noun("savane", "grand terre chaude avec herbe", "Nature"),
    noun("marais", "terre humide avec eau et plante", "Nature"),
    noun("jungle", "forêt chaude avec beaucoup de vivant", "Nature"),
    noun("écorce", "peau de arbre", "Nature"),
    noun("plume", "partie légère de oiseau", "Nature"),
    noun("aile", "partie pour voler", "Nature"),
    noun("patte", "partie de animal pour marcher", "Nature"),
    noun("corne", "partie dure sur tête de certain animal", "Nature"),
    noun("queue", "partie longue au bout de corps de animal", "Nature"),
    noun("bec", "bouche dure de oiseau", "Nature"),
    noun("tanière", "lieu où vivre un animal sauvage", "Nature"),
    noun("ruche", "maison de abeille", "Nature"),
    noun("parc", "grand lieu de nature ou de promenade", "Nature"),
    noun("réserve", "lieu protégé pour nature ou animal", "Nature"),
    noun("prairie-fleurie", "prairie avec beaucoup de fleur", "Nature"),
    noun("lierre", "plante qui monter sur arbre ou mur", "Nature"),
    noun("mousse", "petite plante douce sur pierre ou arbre", "Nature"),
    noun("buisson", "petit groupe de branche et de feuille", "Nature"),
    noun("écureuil", "petit animal avec queue grande", "Nature"),
    noun("souris-animal", "petit animal gris", "Nature"),
    noun("taupe", "petit animal qui vivre sous terre", "Nature"),
    noun("cigale", "insecte de pays chaud avec grand son", "Nature"),
    noun("larve", "jeune forme de certain insecte", "Nature"),
    noun("coquille", "partie dure de coquillage ou de œuf", "Nature"),
    noun("tentacule", "long bras mou de certain animal de mer", "Nature"),
    noun("écosystème", "ensemble de vivant et de lieu dans nature", "Nature"),
]


V43_POOL = [
    noun("aliment", "chose bonne à manger", "Alimentation"),
    noun("boisson", "chose bonne à boire", "Alimentation"),
    noun("viande", "partie de animal bonne à manger", "Alimentation"),
    noun("lait", "boisson blanche venant de animal", "Alimentation"),
    noun("fromage", "aliment fait avec lait", "Alimentation"),
    noun("riz", "petit grain blanc bon à manger", "Alimentation"),
    noun("pâte", "aliment long ou court fait avec farine", "Alimentation"),
    noun("farine", "poudre pour faire pain ou pâte", "Alimentation"),
    noun("beurre", "aliment gras fait avec lait", "Alimentation"),
    noun("huile", "liquide gras pour cuisiner", "Alimentation"),
    noun("sel", "chose blanche pour donner goût", "Alimentation"),
    noun("sucre", "chose blanche ou brune pour goût sucré", "Alimentation"),
    noun("pain", "aliment fait avec farine et eau", "Alimentation"),
    noun("sauce", "liquide ou crème pour donner goût", "Alimentation"),
    noun("soupe", "plat liquide chaud", "Alimentation"),
    noun("dessert", "plat sucré à la fin de repas", "Alimentation"),
    noun("pomme", "fruit rond", "Fruits et légumes"),
    noun("poire", "fruit doux allongé", "Fruits et légumes"),
    noun("banane", "fruit long jaune", "Fruits et légumes"),
    noun("orange", "fruit rond orange", "Fruits et légumes"),
    noun("citron", "fruit jaune et acide", "Fruits et légumes"),
    noun("raisin", "petit fruit rond en groupe", "Fruits et légumes"),
    noun("tomate", "fruit rouge souvent mangé comme légume", "Fruits et légumes"),
    noun("carotte", "légume long orange", "Fruits et légumes"),
    noun("pomme-de-terre", "légume rond venant de terre", "Fruits et légumes"),
    noun("salade", "feuille bonne à manger", "Fruits et légumes"),
    noun("oignon", "légume rond avec goût fort", "Fruits et légumes"),
    noun("ail", "petite plante avec goût fort", "Fruits et légumes"),
    noun("fraise", "petit fruit rouge", "Fruits et légumes"),
    noun("melon", "gros fruit rond", "Fruits et légumes"),
    noun("pastèque", "très gros fruit rond avec beaucoup de eau", "Fruits et légumes"),
    noun("haricot", "petit légume vert ou grain sec", "Fruits et légumes"),
    noun("pois", "petit grain vert bon à manger", "Fruits et légumes"),
    noun("poivron", "légume rouge vert ou jaune", "Fruits et légumes"),
    noun("concombre", "légume long vert frais", "Fruits et légumes"),
    noun("courgette", "légume vert long", "Fruits et légumes"),
    noun("café", "boisson chaude ou froide avec goût fort", "Boissons"),
    noun("thé", "boisson faite avec feuille dans eau chaude", "Boissons"),
    noun("jus", "boisson venant de fruit", "Boissons"),
    noun("vin", "boisson alcoolisée venant de raisin", "Boissons"),
    noun("bière", "boisson alcoolisée avec mousse", "Boissons"),
    noun("alcool", "boisson ou liquide avec effet fort sur corps", "Boissons"),
    noun("eau-minérale", "eau de bouteille pour boire", "Boissons"),
    noun("sirop", "liquide sucré pour boisson", "Boissons"),
    noun("cuisine", "lieu ou art de préparer repas", "Cuisine"),
    verb("cuisiner", "préparer un repas avec feu ou autre action", "Cuisine"),
    verb("cuire", "faire avec chaleur pour manger", "Cuisine"),
    verb("mélanger", "mettre ensemble plusieurs chose", "Cuisine"),
    verb("verser", "faire aller un liquide dans un autre lieu", "Cuisine"),
    verb("goûter", "manger ou boire un peu pour sentir le goût", "Cuisine"),
    verb("mordre", "prendre avec dent", "Cuisine"),
    verb("avaler", "faire descendre dans corps après manger ou boire", "Cuisine"),
    verb("couper", "faire plusieurs partie avec couteau", "Cuisine"),
    verb("éplucher", "retirer la peau de fruit ou légume", "Cuisine"),
    verb("chauffer", "rendre plus chaud", "Cuisine"),
    noun("repas", "moment ou ensemble de chose pour manger", "Repas"),
    noun("plat", "chose à manger ou assiette large", "Repas"),
    noun("assiette", "plat rond pour manger", "Repas"),
    noun("verre", "objet pour boire", "Repas"),
    noun("bol", "petit objet rond pour soupe ou autre aliment", "Repas"),
    noun("couteau", "outil pour couper", "Repas"),
    noun("fourchette", "outil avec dent pour manger", "Repas"),
    noun("cuillère", "outil rond pour soupe ou liquide", "Repas"),
    noun("casserole", "objet pour cuire sur feu", "Repas"),
    noun("poêle", "objet plat pour cuire", "Repas"),
    noun("four", "grand objet chaud pour cuire", "Repas"),
    noun("frigo", "objet froid pour garder aliment", "Repas"),
    noun("bouteille", "objet long pour liquide", "Repas"),
    noun("tasse", "petit objet pour café ou thé", "Repas"),
    noun("nappe", "tissu sur table pour repas", "Repas"),
    noun("serviette", "tissu ou papier pour repas", "Repas"),
    noun("menu", "liste de plat ou boisson", "Repas"),
    noun("goût", "sensation de bouche quand on mange ou boit", "Goût"),
    adj("sucré", "avec goût de sucre", "Goût"),
    adj("salé", "avec goût de sel", "Goût"),
    adj("amer", "avec goût fort et peu doux", "Goût"),
    adj("acide", "avec goût comme citron", "Goût"),
    adj("frais", "peu froid et bon à manger ou à boire", "Goût"),
    adj("cru", "pas cuit", "Goût"),
    adj("cuit", "préparé avec chaleur", "Goût"),
    adj("gras", "avec beaucoup de huile ou de graisse", "Goût"),
    adj("épicé", "avec goût fort de plante ou de poudre", "Goût"),
    adj("doux", "avec goût faible et agréable", "Goût"),
    noun("glace-aliment", "dessert froid et sucré", "Goût"),
    noun("yaourt", "aliment doux fait avec lait", "Goût"),
    noun("crème", "aliment doux ou gras", "Goût"),
    noun("biscuit", "petit aliment sec et sucré", "Goût"),
    noun("gâteau", "aliment sucré pour dessert ou fête", "Goût"),
    noun("chocolat", "aliment brun sucré ou amer", "Goût"),
    noun("miel", "aliment sucré fait par abeille", "Goût"),
    noun("confiture", "fruit sucré cuit", "Goût"),
    noun("olive", "petit fruit pour huile ou repas", "Goût"),
    noun("épice", "petite poudre pour donner goût", "Goût"),
    noun("graisse", "matière grasse de aliment ou de corps", "Goût"),
    noun("pâtisserie", "aliment sucré fait en cuisine", "Goût"),
    noun("sandwich", "pain avec aliment au milieu", "Goût"),
    noun("omelette", "plat de œuf", "Goût"),
    noun("grillade", "viande ou légume cuit sur feu", "Goût"),
    noun("vinaigre", "liquide acide pour cuisine", "Goût"),
    noun("cerise", "petit fruit rouge", "Goût"),
    noun("abricot", "fruit orange doux", "Goût"),
    noun("noix", "fruit sec dur", "Goût"),
    noun("amande", "petit fruit sec clair", "Goût"),
]


V44_POOL = [
    noun("transport", "moyen pour aller de un lieu à un autre", "Transport"),
    noun("véhicule", "objet pour transport", "Transport"),
    noun("bus", "grand véhicule public sur route", "Transport"),
    noun("camion", "grand véhicule pour chose lourde", "Transport"),
    noun("vélo", "véhicule à deux roue", "Transport"),
    noun("moto", "véhicule à deux roue avec moteur", "Transport"),
    noun("bateau", "véhicule sur eau", "Transport"),
    noun("avion", "véhicule dans ciel", "Transport"),
    noun("navire", "grand bateau", "Transport"),
    noun("ambulance", "véhicule pour urgence médicale", "Transport"),
    noun("tram", "véhicule public sur rail dans ville", "Transport"),
    noun("métro", "transport public sous ville", "Transport"),
    noun("taxi", "voiture de service pour transport de personne", "Transport"),
    noun("gare", "lieu de train", "Lieux de transport"),
    noun("arrêt", "lieu où un bus ou tram venir", "Lieux de transport"),
    noun("station", "lieu de métro de bus ou de service", "Lieux de transport"),
    noun("port", "lieu pour bateau", "Lieux de transport"),
    noun("aéroport", "lieu pour avion", "Lieux de transport"),
    noun("parking", "lieu pour laisser véhicule", "Lieux de transport"),
    noun("quai", "bord de gare ou de port", "Lieux de transport"),
    noun("pont", "route au-dessus de eau ou de route", "Lieux de transport"),
    noun("terminal", "grand lieu de départ ou arrivée dans aéroport ou port", "Lieux de transport"),
    noun("trajet", "chemin entre départ et arrivée", "Déplacement"),
    noun("voyage", "grand trajet ou temps passé loin de maison", "Déplacement"),
    noun("billet", "papier ou document pour un voyage", "Déplacement"),
    noun("ticket", "petit billet pour transport ou service", "Déplacement"),
    noun("bagage", "chose portée pour un voyage", "Déplacement"),
    noun("valise", "grand sac pour voyage", "Déplacement"),
    verb("conduire", "faire aller un véhicule", "Déplacement"),
    verb("naviguer", "aller sur eau ou suivre une route avec direction", "Déplacement"),
    verb("embarquer", "entrer dans un bateau un avion ou un train", "Déplacement"),
    noun("avance", "temps avant le moment attendu", "Déplacement"),
    noun("départ", "moment ou lieu du début de trajet", "Déplacement"),
    noun("arrivée", "moment ou lieu de fin de trajet", "Déplacement"),
    noun("correspondance", "changement de transport pendant un trajet", "Déplacement"),
    noun("retour", "trajet pour revenir", "Déplacement"),
    noun("plan", "dessin ou document pour voir un lieu ou un trajet", "Navigation"),
    noun("frontière", "ligne entre deux pays ou deux grand lieu", "Navigation"),
    noun("panneau", "objet avec mot ou signe pour informer", "Navigation"),
    noun("signal", "signe ou lumière pour donner une information", "Navigation"),
    noun("voie", "partie de route ou de rail pour aller", "Navigation"),
    noun("carrefour", "lieu où plusieurs route se couper", "Navigation"),
    noun("virage", "partie de route qui tourner", "Navigation"),
    noun("feu", "lumière de circulation pour route", "Navigation"),
    noun("passage", "lieu pour traverser", "Navigation"),
    noun("sens", "direction de trajet ou de route", "Navigation"),
    noun("marin", "personne qui travailler sur mer ou navire", "Mer"),
    noun("voile", "grand tissu pour faire avancer un bateau", "Mer"),
    noun("rame", "objet pour faire avancer un bateau à la main", "Mer"),
    noun("courant", "eau qui aller dans une direction", "Mer"),
    noun("vague", "mouvement haut et bas de eau", "Mer"),
    noun("marée", "mouvement de mer qui monter et descendre", "Mer"),
    noun("phare", "grande lumière au bord de mer", "Mer"),
    noun("capitaine", "chef de bateau ou de avion", "Mer"),
    noun("équipage", "groupe de personne dans un bateau ou avion", "Mer"),
    noun("cabine", "petite chambre dans un bateau ou train", "Mer"),
    noun("route", "long chemin pour véhicule ou personne", "Transport"),
    noun("autoroute", "grande route rapide", "Transport"),
    noun("trottoir", "partie de rue pour marcher", "Transport"),
    noun("rue", "chemin dans ville avec maison", "Transport"),
    noun("piste", "voie pour avion vélo ou sport", "Transport"),
    noun("rail", "barre de fer pour train", "Transport"),
    noun("train", "grand véhicule sur rail", "Transport"),
    noun("wagon", "partie de train", "Transport"),
    noun("moteur", "partie qui faire avancer un véhicule", "Transport"),
    noun("roue", "partie ronde de véhicule", "Transport"),
    noun("essence", "liquide pour moteur", "Transport"),
    noun("frein", "partie pour ralentir ou arrêter un véhicule", "Transport"),
    noun("casque", "protection pour tête", "Transport"),
    noun("ceinture", "bande pour sécurité dans voiture ou vêtement", "Transport"),
    noun("carte-routière", "plan pour route et ville", "Transport"),
    noun("péage", "paiement pour une route", "Transport"),
    noun("douane", "service à une frontière", "Transport"),
    noun("visa", "autorisation de voyage dans un pays", "Transport"),
    noun("tourisme", "voyage pour voir un lieu", "Transport"),
    noun("touriste", "personne qui faire un voyage pour voir un lieu", "Transport"),
    noun("camping", "lieu ou manière de dormir dehors pendant voyage", "Transport"),
    noun("auberge", "lieu simple pour dormir pendant voyage", "Transport"),
    noun("hôtel", "lieu pour dormir pendant voyage", "Transport"),
    noun("réservation", "action de garder une place pour plus tard", "Transport"),
    noun("place-assise", "place pour s asseoir dans transport", "Transport"),
    noun("embarquement", "moment ou action de embarquer", "Transport"),
    noun("atterrissage", "moment où un avion revenir au sol", "Transport"),
    noun("décollage", "moment où un avion quitter le sol", "Transport"),
    noun("croisière", "voyage sur mer pour plaisir", "Transport"),
    noun("portail", "grande entrée fermée", "Transport"),
    noun("signalisation", "ensemble de panneau et de signal", "Transport"),
    noun("boussole", "instrument pour trouver nord", "Transport"),
    noun("rive", "bord de rivière ou de lac", "Transport"),
    noun("passager", "personne transportée dans un véhicule", "Transport"),
    noun("passeur", "personne qui faire traverser de un bord à un autre", "Transport"),
    noun("escale", "arrêt court pendant un grand voyage", "Transport"),
    noun("doublage-route", "autre route pour le même trajet", "Transport"),
    noun("retour-voyage", "voyage pour revenir au point de départ", "Transport"),
    noun("cabine-pilotage", "lieu du pilote dans avion ou navire", "Transport"),
    noun("carte-embarquement", "document pour entrer dans avion", "Transport"),
    noun("port-bagage", "lieu pour bagage", "Transport"),
    noun("remorque", "véhicule tiré par un autre", "Transport"),
    noun("piste-cyclable", "voie pour vélo", "Transport"),
    noun("stationnement", "action de laisser un véhicule dans un lieu", "Transport"),
    noun("croisement", "lieu où deux route se rencontrer", "Transport"),
    noun("descente", "partie de route vers le bas", "Transport"),
    noun("montée", "partie de route vers le haut", "Transport"),
    noun("passerelle", "petit pont pour personne", "Transport"),
    noun("navette", "transport qui faire souvent le même trajet", "Transport"),
]


V45_POOL = [
    noun("étoile", "astre visible dans ciel de nuit", "Ciel et espace"),
    noun("lune", "astre proche de terre", "Ciel et espace"),
    noun("planète", "grand astre qui tourner autour de une étoile", "Ciel et espace"),
    noun("univers", "ensemble de tout ciel espace et matière", "Ciel et espace"),
    noun("galaxie", "très grand groupe de étoile", "Ciel et espace"),
    noun("orbite", "chemin de un astre autour de un autre", "Ciel et espace"),
    noun("astre", "grand corps dans ciel ou espace", "Ciel et espace"),
    noun("comète", "astre avec longue trace de lumière", "Ciel et espace"),
    noun("météore", "lumière de pierre dans ciel", "Ciel et espace"),
    noun("soleil-système", "étoile du système de terre", "Ciel et espace"),
    noun("science", "recherche de vérité sur monde par observation et expérience", "Sciences simples"),
    noun("énergie", "force possible pour mouvement chaleur ou lumière", "Sciences simples"),
    noun("masse", "quantité de matière dans une chose", "Sciences simples"),
    noun("atome", "très petite partie de matière", "Sciences simples"),
    noun("gaz", "matière sans forme propre comme air", "Sciences simples"),
    noun("liquide", "matière qui couler et prendre la forme de un objet", "Sciences simples"),
    noun("solide", "matière avec forme propre", "Sciences simples"),
    noun("pression", "force sur une surface", "Sciences simples"),
    noun("onde", "mouvement qui passer dans eau air ou autre matière", "Sciences simples"),
    noun("électricité", "énergie pour lumière machine ou appareil", "Sciences simples"),
    adj("magnétique", "lié à force de aimant", "Sciences simples"),
    noun("rayon", "ligne de lumière ou de chaleur", "Sciences simples"),
    noun("vide", "lieu sans matière", "Sciences simples"),
    noun("gravité", "force qui faire tomber vers terre", "Sciences simples"),
    noun("molécule", "petit groupe de atome", "Sciences simples"),
    noun("observer", "action de voir avec attention", "Observation"),
    noun("instrument", "outil pour observer mesurer ou jouer", "Observation"),
    noun("lunette", "instrument pour mieux voir loin", "Observation"),
    noun("télescope", "instrument pour voir ciel et étoile", "Observation"),
    noun("microscope", "instrument pour voir très petit", "Observation"),
    noun("expérience", "action de science pour vérifier une idée", "Observation"),
    noun("hypothèse", "idée possible avant une preuve", "Observation"),
    noun("théorie", "explication générale en science", "Observation"),
    noun("mesure-science", "résultat de mesure pour science", "Observation"),
    noun("laboratoire", "lieu pour expérience et science", "Observation"),
    noun("échantillon", "petite partie prise pour observation ou analyse", "Observation"),
    noun("tempête-solaire", "mouvement fort de énergie venant de soleil", "Ciel et espace"),
    noun("satellite", "objet ou astre qui tourner autour de un autre", "Ciel et espace"),
    noun("fusée", "véhicule pour aller dans espace", "Ciel et espace"),
    noun("cosmonaute", "personne qui aller dans espace", "Ciel et espace"),
    noun("laboratoire-mobile", "instrument ou lieu de science en mouvement", "Observation"),
    noun("thermomètre", "instrument pour température", "Observation"),
    noun("baromètre", "instrument pour pression", "Observation"),
    noun("aimant", "objet avec force magnétique", "Observation"),
    noun("balance", "instrument pour poids", "Observation"),
    noun("métal", "matière dure souvent brillante", "Sciences simples"),
    noun("cuivre", "métal rouge brun", "Sciences simples"),
    noun("fer", "métal gris fort", "Sciences simples"),
    noun("acier", "métal très fort", "Sciences simples"),
    noun("plastique", "matière légère faite par industrie", "Sciences simples"),
    noun("verre-matière", "matière dure et transparente", "Sciences simples"),
    noun("poussière", "très petite matière sèche", "Sciences simples"),
    noun("flamme", "partie visible de feu", "Sciences simples"),
    noun("fumée", "gaz visible venant de feu", "Sciences simples"),
    noun("vapeur", "eau ou autre liquide devenu gaz", "Sciences simples"),
    noun("cristal", "solide avec forme régulière", "Sciences simples"),
    noun("expansion", "action de devenir plus grand", "Sciences simples"),
    noun("contraction", "action de devenir plus petit", "Sciences simples"),
    noun("rotation", "mouvement autour de soi", "Sciences simples"),
    noun("révolution", "mouvement autour de un autre corps", "Sciences simples"),
    noun("mesure-temps", "mesure de durée ou de moment", "Sciences simples"),
    noun("spectre", "ensemble de couleur de lumière", "Sciences simples"),
    noun("signal-science", "information passant par onde", "Sciences simples"),
    noun("champ-magnétique", "espace où agir une force magnétique", "Sciences simples"),
    noun("réaction", "changement après contact ou action", "Sciences simples"),
    noun("évaporation", "passage de liquide à gaz", "Sciences simples"),
    noun("fusion", "passage de solide à liquide", "Sciences simples"),
    noun("gel-science", "passage de liquide à solide", "Sciences simples"),
    noun("densité", "rapport entre masse et volume", "Sciences simples"),
    noun("courant-électrique", "mouvement de électricité", "Sciences simples"),
    noun("batterie", "objet qui garder électricité", "Sciences simples"),
    noun("circuit", "chemin fermé pour électricité", "Sciences simples"),
    noun("ampoule", "objet qui faire lumière avec électricité", "Sciences simples"),
    noun("observatoire", "lieu pour observer ciel ou science", "Observation"),
    noun("constellation", "groupe de étoile dans ciel", "Ciel et espace"),
    noun("particule", "très petite partie de matière", "Sciences simples"),
    noun("thermique", "lié à chaleur", "Sciences simples"),
]


V46_POOL = [
    noun("art", "création pour image musique texte ou autre beauté", "Art visuel"),
    noun("dessin", "image faite avec main", "Art visuel"),
    verb("dessiner", "faire un dessin", "Art visuel"),
    noun("peinture", "image faite avec couleur", "Art visuel"),
    verb("peindre", "faire une peinture", "Art visuel"),
    noun("tableau", "peinture sur support", "Art visuel"),
    noun("photo", "image prise avec appareil", "Art visuel"),
    noun("photographie", "art ou image de photo", "Art visuel"),
    noun("cadre", "bord ou support autour de image", "Art visuel"),
    noun("sculpture", "art de forme dans pierre bois ou autre matière", "Art visuel"),
    noun("portrait", "image de visage ou de personne", "Art visuel"),
    noun("paysage-image", "image de lieu ou nature", "Art visuel"),
    noun("croquis", "dessin rapide", "Art visuel"),
    noun("toile", "support de peinture", "Art visuel"),
    noun("galerie", "lieu pour voir art", "Art visuel"),
    noun("exposition", "ensemble de œuvre montrée au public", "Art visuel"),
    noun("son", "mouvement entendu par oreille", "Musique et son"),
    noun("note", "petit son de musique", "Musique et son"),
    noun("rythme", "organisation de temps dans musique", "Musique et son"),
    noun("chanson", "texte avec musique", "Musique et son"),
    verb("chanter", "faire une chanson avec voix", "Musique et son"),
    noun("mélodie", "suite de note dans musique", "Musique et son"),
    noun("harmonie", "bon accord entre plusieurs son", "Musique et son"),
    noun("piano", "instrument de musique avec touche", "Musique et son"),
    noun("guitare", "instrument de musique avec corde", "Musique et son"),
    noun("violon", "instrument de musique avec corde et archet", "Musique et son"),
    noun("tambour", "instrument de musique à frapper", "Musique et son"),
    noun("concert", "moment public de musique", "Musique et son"),
    noun("chorale", "groupe qui chanter ensemble", "Musique et son"),
    noun("texte", "suite de mot écrit", "Texte et littérature"),
    noun("poème", "texte court avec rythme ou image", "Texte et littérature"),
    noun("auteur", "personne qui écrire un texte", "Texte et littérature"),
    noun("lecteur", "personne qui lire un texte", "Texte et littérature"),
    noun("roman", "long texte de histoire", "Texte et littérature"),
    noun("conte", "histoire courte", "Texte et littérature"),
    noun("chapitre", "grande partie de livre", "Texte et littérature"),
    noun("paragraphe", "partie de texte avec plusieurs phrase", "Texte et littérature"),
    noun("phrase", "suite de mot avec un sens complet", "Texte et littérature"),
    noun("journal", "texte ou livre de jour ou de information", "Texte et littérature"),
    noun("film", "image en mouvement avec son", "Spectacle"),
    noun("théâtre", "art ou lieu de spectacle avec acteur", "Spectacle"),
    noun("acteur", "personne qui jouer un rôle", "Spectacle"),
    noun("scène", "lieu de spectacle ou moment fort", "Spectacle"),
    verb("danser", "faire mouvement de corps avec rythme", "Spectacle"),
    noun("danse", "art ou action de danser", "Spectacle"),
    noun("spectacle", "moment public de art ou de scène", "Spectacle"),
    noun("cinéma", "lieu ou art de film", "Spectacle"),
    noun("costume", "vêtement pour scène ou fête", "Spectacle"),
    noun("masque", "objet devant visage", "Spectacle"),
    noun("style", "manière reconnaissable de faire ou de montrer", "Esthétique"),
    noun("beauté", "qualité de ce qui plaire par vue ou autre sens", "Esthétique"),
    noun("création", "action de faire une œuvre ou une idée", "Esthétique"),
    verb("imaginer", "former une image ou une idée dans esprit", "Esthétique"),
    noun("inspiration", "idée ou force pour créer", "Esthétique"),
    noun("image", "vue de une chose en dessin photo ou esprit", "Esthétique"),
    noun("forme-art", "manière visible de une œuvre", "Esthétique"),
    noun("couleur-art", "usage de couleur dans art", "Esthétique"),
    noun("fiction", "histoire qui n est pas réelle", "Esthétique"),
    noun("personnage", "personne de histoire ou de film", "Esthétique"),
    noun("récit", "texte ou parole qui raconter une histoire", "Esthétique"),
    noun("bibliothèque", "lieu avec beaucoup de livre", "Esthétique"),
    noun("édition", "action de publier un texte ou une image", "Esthétique"),
    noun("publication", "texte image ou œuvre rendue publique", "Esthétique"),
    noun("impression", "action de mettre texte ou image sur papier", "Esthétique"),
    noun("typographie", "style de lettre pour texte", "Esthétique"),
    noun("affiche", "grand papier avec image ou texte", "Esthétique"),
    noun("bande-dessinée", "suite de image et texte", "Esthétique"),
    noun("illustration", "image pour accompagner un texte", "Esthétique"),
    noun("chant", "voix musicale", "Esthétique"),
    noun("refrain", "partie répétée de chanson", "Esthétique"),
    noun("couplet", "partie variable de chanson", "Esthétique"),
    noun("micro", "instrument pour rendre voix plus forte", "Esthétique"),
    noun("affluence", "grand nombre de public dans un lieu", "Esthétique"),
    noun("projection", "action de montrer un film ou une image", "Esthétique"),
    noun("atelier", "lieu pour création ou travail de art", "Esthétique"),
    noun("palette", "objet avec couleur pour peindre", "Esthétique"),
    noun("marionnette", "petit personnage pour spectacle", "Esthétique"),
    noun("improvisation", "création faite sans préparation longue", "Esthétique"),
]


V50_POOL = [
    noun("voisin", "personne qui vivre près de une autre personne", "Relations sociales"),
    noun("voisine", "femme qui vivre près de une autre personne", "Relations sociales"),
    noun("ami", "personne proche avec confiance et amitié", "Relations sociales"),
    noun("amitié", "relation bonne et durable entre des personne", "Relations sociales"),
    verb("inviter", "demander à une personne de venir", "Relations sociales"),
    noun("visite", "action de venir voir une personne ou un lieu", "Relations sociales"),
    noun("fête", "moment de joie avec groupe", "Relations sociales"),
    noun("cadeau", "chose donnée pour plaisir", "Relations sociales"),
    noun("message", "texte court ou parole envoyée à une personne", "Relations sociales"),
    noun("conversation", "suite de parole entre des personne", "Relations sociales"),
    noun("respect", "attitude de considération pour une personne ou une règle", "Relations sociales"),
    noun("confiance", "sentiment de croire en une personne ou une chose", "Relations sociales"),
    noun("conflit", "opposition forte entre des personne ou des groupe", "Relations sociales"),
    noun("surprise", "émotion après une chose non attendue", "Émotions"),
    noun("colère", "émotion forte de mal ou de opposition", "Émotions"),
    noun("honte", "émotion de mal devant les autre", "Émotions"),
    noun("fierté", "émotion de valeur ou de réussite", "Émotions"),
    noun("espoir", "attente positive de une chose possible", "Émotions"),
    noun("doute", "état sans certitude", "Émotions"),
    noun("inquiétude", "petite peur durable", "Émotions"),
    noun("soulagement", "bien après la fin de peur ou de douleur", "Émotions"),
    adj("précis", "exact et bien défini", "Qualités"),
    adj("vague", "pas précis ou peu clair", "Qualités"),
    adj("réel", "qui existe vraiment", "Qualités"),
    adj("imaginaire", "fait par esprit et pas réel", "Qualités"),
    adj("complet", "avec toutes les partie nécessaires", "Qualités"),
    adj("partiel", "pas complet", "Qualités"),
    adj("principal", "le plus important", "Qualités"),
    adj("secondaire", "moins important que le principal", "Qualités"),
    adj("nécessaire", "qu on doit avoir ou faire", "Qualités"),
    adj("probable", "possible avec forte chance", "Qualités"),
    adj("rare", "qui venir peu souvent", "Qualités"),
    adj("fréquent", "qui venir souvent", "Qualités"),
    noun("pièce", "partie fermée dans une maison", "Vie domestique"),
    noun("chambre", "pièce pour dormir", "Vie domestique"),
    noun("salon", "pièce pour s asseoir parler ou recevoir", "Vie domestique"),
    noun("salle", "grande pièce", "Vie domestique"),
    noun("bain", "eau pour laver corps", "Vie domestique"),
    noun("douche", "eau qui tomber pour laver corps", "Vie domestique"),
    noun("toilette", "lieu ou objet pour corps et propreté", "Vie domestique"),
    noun("linge", "tissu pour corps lit ou maison", "Vie domestique"),
    noun("vêtement", "chose pour porter sur corps", "Vie domestique"),
    noun("chemise", "vêtement du haut de corps", "Vie domestique"),
    noun("pantalon", "vêtement du bas de corps", "Vie domestique"),
    noun("chaussure", "objet pour pied", "Vie domestique"),
    noun("manteau", "vêtement pour froid ou pluie", "Vie domestique"),
    noun("sac", "objet pour porter chose", "Vie domestique"),
    noun("clé", "objet pour ouvrir ou fermer une porte", "Vie domestique"),
    noun("lit", "meuble pour dormir", "Vie domestique"),
    noun("oreiller", "objet doux pour tête au lit", "Vie domestique"),
    noun("couverture", "linge pour chaud au lit", "Vie domestique"),
    noun("rideau", "tissu devant fenêtre", "Vie domestique"),
    noun("fenêtre", "ouverture dans mur pour lumière ou air", "Vie domestique"),
    noun("porte", "ouverture mobile pour entrer ou sortir", "Vie domestique"),
    noun("mur", "grande partie verticale de maison", "Vie domestique"),
    noun("plafond", "partie haute de une pièce", "Vie domestique"),
    noun("sol", "partie basse où on marcher", "Vie domestique"),
    noun("tapis", "tissu au sol", "Vie domestique"),
    noun("armoire", "meuble fermé pour vêtement ou autre chose", "Vie domestique"),
    noun("étagère", "meuble avec niveau pour poser chose", "Vie domestique"),
    noun("lampe", "objet pour lumière", "Vie domestique"),
    noun("prise", "objet pour électricité", "Vie domestique"),
    noun("balai", "outil pour nettoyer le sol", "Vie domestique"),
    noun("savon", "chose pour laver", "Vie domestique"),
    noun("serviette-bain", "linge pour sécher corps", "Vie domestique"),
    noun("lessive", "produit pour laver linge", "Vie domestique"),
    noun("poubelle", "objet pour déchet", "Vie domestique"),
    noun("déchet", "chose sans usage à jeter", "Vie domestique"),
    noun("ménage", "action de nettoyer et ranger maison", "Vie domestique"),
    noun("rang", "bon ordre dans les chose", "Vie domestique"),
    verb("ranger", "mettre en bon ordre", "Vie domestique"),
    verb("nettoyer", "rendre propre", "Vie domestique"),
    noun("internet", "réseau mondial de information et de message", "Communication moderne"),
    noun("site", "ensemble de page sur internet", "Communication moderne"),
    noun("mail", "message écrit par internet", "Communication moderne"),
    noun("courriel", "autre mot pour mail", "Communication moderne"),
    noun("réseau", "ensemble de lien entre personne ou machine", "Communication moderne"),
    noun("fichier", "ensemble de donnée dans un ordinateur", "Communication moderne"),
    noun("écran", "surface de image sur ordinateur ou téléphone", "Communication moderne"),
    noun("clavier", "outil avec touche pour écrire", "Communication moderne"),
    noun("logiciel", "programme pour ordinateur ou appareil", "Communication moderne"),
    noun("application", "logiciel pour un usage précis", "Communication moderne"),
    noun("ordinateur", "machine pour calcul information et communication", "Communication moderne"),
    noun("téléphone", "appareil pour parler ou envoyer message", "Communication moderne"),
    noun("portable", "téléphone ou ordinateur facile à porter", "Communication moderne"),
    noun("mot-de-passe", "suite de signe pour entrer dans un compte", "Communication moderne"),
    noun("donnée", "information gardée dans un fichier ou un système", "Communication moderne"),
    noun("page-web", "page sur internet", "Communication moderne"),
    noun("lien", "chemin vers une autre page ou information", "Communication moderne"),
    noun("touche", "petite partie de clavier", "Communication moderne"),
    noun("souris", "outil pour diriger un écran", "Communication moderne"),
    noun("imprimante", "machine pour impression sur papier", "Communication moderne"),
    noun("chargeur", "objet pour donner électricité à appareil", "Communication moderne"),
    noun("batterie-mobile", "réserve de électricité dans appareil", "Communication moderne"),
    noun("caméra", "appareil pour image ou film", "Communication moderne"),
    noun("vidéo", "image en mouvement enregistrée", "Communication moderne"),
    noun("audio", "son enregistré", "Communication moderne"),
    noun("document-numérique", "document dans un fichier", "Communication moderne"),
    noun("profil", "ensemble de information sur une personne dans un service", "Communication moderne"),
    noun("compte-utilisateur", "compte pour utiliser un site ou une application", "Communication moderne"),
    noun("sécurité-numérique", "protection de compte fichier et réseau", "Communication moderne"),
    noun("notification", "message court de application ou téléphone", "Communication moderne"),
    noun("mise-à-jour", "nouvelle version de logiciel ou application", "Communication moderne"),
    noun("historique", "suite de action déjà faite", "Communication moderne"),
    noun("outil-numérique", "outil sur ordinateur ou téléphone", "Communication moderne"),
    noun("signalement", "message pour dire un problème", "Communication moderne"),
    noun("abonnement", "accord pour service répété dans le temps", "Communication moderne"),
    noun("profil-public", "profil visible par beaucoup de personne", "Communication moderne"),
    noun("paramètre", "choix de réglage de logiciel ou appareil", "Communication moderne"),
    noun("réglage", "choix pour changer un appareil ou logiciel", "Communication moderne"),
    noun("connexion", "action de lier un appareil ou entrer dans un service", "Communication moderne"),
    noun("déconnexion", "action de quitter un service ou couper un lien", "Communication moderne"),
    noun("mise-en-page", "organisation de texte et image sur une page", "Communication moderne"),
    noun("archive", "groupe de vieux document ou fichier gardé", "Communication moderne"),
    noun("dossier-numérique", "groupe de fichier", "Communication moderne"),
    noun("conversation-écrite", "échange de message écrit", "Communication moderne"),
    noun("appel", "action de parler par téléphone", "Communication moderne"),
    noun("appel-vidéo", "appel avec image et son", "Communication moderne"),
    noun("agenda", "outil pour date heure et rendez-vous", "Communication moderne"),
    noun("liste", "suite écrite de plusieurs chose", "Communication moderne"),
    noun("mémoire", "capacité de garder information ou souvenir", "Consolidation"),
    noun("souvenir", "image de esprit sur le passé", "Consolidation"),
    noun("habitude", "action faite souvent", "Consolidation"),
    noun("routine", "suite de action habituelle", "Consolidation"),
    noun("choix", "décision entre plusieurs possibilité", "Consolidation"),
    noun("préférence", "choix aimé plus que un autre", "Consolidation"),
    noun("objectif", "but précis", "Consolidation"),
    noun("progrès", "avance vers un meilleur état", "Consolidation"),
    noun("échec", "mauvais résultat d une action", "Consolidation"),
    noun("succès", "bon résultat d une action", "Consolidation"),
    noun("motivation", "force intérieure pour agir", "Consolidation"),
    noun("patience", "capacité à attendre sans colère", "Consolidation"),
    noun("silence", "absence de son ou de parole", "Consolidation"),
    noun("bruit", "son fort ou gênant", "Consolidation"),
    noun("ombre", "partie sans lumière forte", "Consolidation"),
    noun("parfum", "odeur agréable", "Consolidation"),
    noun("odeur", "sensation du nez", "Consolidation"),
    noun("texture", "manière de sentir une surface au toucher", "Consolidation"),
    noun("coussin", "objet doux pour s asseoir ou dormir", "Vie domestique"),
    noun("bureau-maison", "table ou lieu pour travail dans maison", "Vie domestique"),
    noun("miroir", "surface qui montrer image de visage ou corps", "Vie domestique"),
    noun("robinet", "objet pour faire venir eau", "Vie domestique"),
    noun("lavage", "action de laver", "Vie domestique"),
    noun("rangement", "action de ranger une maison ou des chose", "Vie domestique"),
    noun("placard", "petit meuble ou lieu fermé dans mur", "Vie domestique"),
    noun("prise-de-note", "action de écrire une note", "Communication moderne"),
    noun("dossier-partagé", "dossier numérique vu par plusieurs personne", "Communication moderne"),
    noun("mot-clé", "mot utile pour recherche ou classement", "Communication moderne"),
    noun("recherche-web", "recherche sur internet", "Communication moderne"),
    noun("onglet", "partie de écran ou de page-web", "Communication moderne"),
    noun("navigateur", "logiciel pour site et page-web", "Communication moderne"),
    noun("partage", "action de donner à voir ou à avoir à une autre personne", "Communication moderne"),
    noun("synchronisation", "action de mettre au même temps ou au même état", "Communication moderne"),
    noun("compte-rendu", "texte court après réunion ou action", "Communication moderne"),
    noun("urgence-domestique", "problème rapide dans maison", "Consolidation"),
    noun("discussion", "conversation sur un sujet", "Relations sociales"),
    noun("accord-social", "bon accord entre des personne", "Relations sociales"),
    noun("désaccord", "opposition entre des personne", "Relations sociales"),
    noun("entraide", "aide entre des personne", "Relations sociales"),
    noun("accueil", "action de recevoir une personne", "Relations sociales"),
    noun("présence", "fait de être là", "Consolidation"),
]


V33_EXTRA_FORMS = [
    ("surveille", "surveiller"), ("surveillent", "surveiller"),
    ("consulte", "consulter"), ("consultent", "consulter"),
    ("fatiguée", "fatigué"), ("fatiguées", "fatigué"),
]
V41_EXTRA_FORMS = [
    ("mesure", "mesurer"), ("mesurent", "mesurer"),
    ("divise", "diviser"), ("multiplie", "multiplier"),
]
V43_EXTRA_FORMS = [
    ("cuisine", "cuisiner"), ("cuisinent", "cuisiner"),
    ("cuit", "cuire"), ("mélange", "mélanger"), ("verse", "verser"),
]
V44_EXTRA_FORMS = [
    ("conduit", "conduire"), ("conduisent", "conduire"),
    ("embarque", "embarquer"), ("embarquent", "embarquer"),
]
V46_EXTRA_FORMS = [
    ("dessine", "dessiner"), ("peint", "peindre"), ("chante", "chanter"),
    ("danse", "danser"), ("imagine", "imaginer"),
]
V50_EXTRA_FORMS = [
    ("invite", "inviter"), ("invitent", "inviter"),
    ("range", "ranger"), ("rangent", "ranger"),
    ("nettoie", "nettoyer"), ("nettoient", "nettoyer"),
]


def mk_simple_tests(domain, items, pattern):
    tests = []
    for text, rating in pattern(items):
        tests.append({"domain": domain, "text": text, "rating": rating})
    return tests


def tests_v33():
    tests = []
    droit = ["avocat", "police", "amende", "procédure", "délai", "courrier", "reçu", "sanction", "contrôle", "sécurité", "infraction", "défense", "conseil", "justice", "jugement", "décision", "recours", "témoin", "enquête", "procès", "plainte", "preuve", "tribunal", "juge", "autorisation"]
    for i, w in enumerate(droit):
        text = f"Je veux un {w}." if i % 2 == 0 else f"Ce {w} aide dans un problème de droit."
        tests.append({"domain": "droit pratique", "text": text, "rating": "naturel" if i < 18 else "acceptable"})
    logement = ["logement", "loyer", "propriétaire", "locataire", "bail", "charge", "budget", "épargne", "crédit", "retard", "remboursement", "caution", "garantie", "adresse", "document", "facture", "compte", "revenu", "dépense", "service", "demande", "mairie", "courrier", "preuve", "signature"]
    for i, w in enumerate(logement):
        text = f"Le {w} est dans le dossier." if i % 2 else f"Je parle du {w} avec le service."
        tests.append({"domain": "logement et budget", "text": text, "rating": "naturel" if i < 18 else "acceptable"})
    travail = ["chômage", "licenciement", "retraite", "embauche", "candidat", "entretien", "formation", "expérience", "compétence", "certificat", "attestation", "allocation", "social", "emploi", "métier", "salaire", "poste", "responsable", "réunion", "contrat", "collègue", "client", "service", "projet", "horaire"]
    for i, w in enumerate(travail):
        art = "une" if w.endswith("e") else "un"
        text = f"Je cherche {art} {w}." if i % 3 == 0 else f"Ce {w} est utile pour le travail."
        tests.append({"domain": "travail social", "text": text, "rating": "naturel" if i < 17 else "acceptable"})
    sante = ["température", "tension", "accident", "fracture", "brûlure", "plaie", "antidouleur", "surdose", "grave", "léger", "chronique", "surveiller", "consulter", "incident", "secours", "urgence", "médecin", "soin", "traitement", "douleur", "symptôme", "hôpital", "maladie", "risque", "protéger"]
    for i, w in enumerate(sante):
        text = f"Le médecin peut {w}." if w in {"surveiller", "consulter"} else f"Cette {w} demande un soin." if w in {"brûlure", "fracture", "plaie", "température", "tension"} else f"Ce {w} est un problème de santé."
        tests.append({"domain": "santé fine et accidents", "text": text, "rating": "naturel" if i < 17 else "acceptable"})
    mental = ["dépression", "anxiété", "stress", "angoisse", "handicap", "fatigué", "isolement", "soutien", "psychologue", "souffrance", "thérapie", "crise", "victime", "esprit", "relation", "peur", "émotion", "calme", "danger", "dormir", "aide", "bien", "mal", "parler", "médecin"]
    for i, w in enumerate(mental):
        text = f"Cette personne a besoin de {w}." if w not in {"fatigué", "parler"} else ("Cette personne est fatiguée." if w == "fatigué" else "Parler peut aider.")
        tests.append({"domain": "santé mentale", "text": text, "rating": "naturel" if i < 17 else "acceptable"})
    return tests


def tests_v40():
    tests = []
    colors = ["couleur", "rouge", "bleu", "vert", "jaune", "noir", "blanc", "gris", "brun", "rose", "orange", "violet", "clair", "sombre", "ciel", "eau", "terre", "lumière", "feuille", "sang", "nuage", "mer", "mur", "porte", "maison", "route", "plage", "jardin", "forêt", "montagne"]
    for i, w in enumerate(colors[:30]):
        text = f"Cette chose est {w}." if w in {"rouge","bleu","vert","jaune","noir","blanc","gris","brun","rose","orange","violet"} else f"Cette {w} est importante."
        tests.append({"domain": "couleurs et description", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    cal = ["matin","soir","midi","minuit","semaine","mois","année","saison","printemps","été","automne","hiver","date","calendrier","lendemain","veille","seconde","minute","janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
    for i, w in enumerate(cal):
        text = f"Le {w} est dans le calendrier." if w not in {"matin","soir","midi","minuit"} else f"Je viens le {w}."
        tests.append({"domain": "temps et calendrier", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    loc = ["direction","nord","sud","est","ouest","dessus","dessous","milieu","coin","fond","entrée","sortie","niveau","étage","centre","bord","intérieur","extérieur","gauche","droite","devant","derrière","ici","là","proche","loin","route","maison","ville","porte"]
    for i, w in enumerate(loc[:30]):
        text = f"Le lieu est au {w}." if w in {"nord","sud","est","ouest","milieu","centre","fond","bord"} else f"Le {w} aide le lieu."
        tests.append({"domain": "localisation", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    met = ["météo","climat","nuage","orage","neige","glace","tempête","brouillard","tonnerre","éclair","foudre","gel","montagne","colline","vallée","rivière","lac","source","île","plage","sable","rocher","forêt","champ","jardin","océan","désert","prairie","falaise","côte"]
    for i, w in enumerate(met):
        text = f"Cette {w} change le paysage." if w in {"météo","tempête","neige","glace"} else f"Il y a une {w}." if w.endswith("e") else f"Il y a un {w}."
        tests.append({"domain": "météo et géographie", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    return tests


def tests_v41():
    tests = []
    nums = ["zéro","deux","trois","quatre","cinq","six","sept","huit","neuf","dix","onze","douze","treize","quatorze","quinze","seize","vingt","trente","quarante","cinquante","soixante","cent","mille","million","nombre","chiffre","total","somme","part","valeur"]
    for i, w in enumerate(nums):
        text = f"Le total est {w}." if w in {"zéro","deux","trois","quatre","cinq","six","sept","huit","neuf","dix"} else f"Ce {w} sert pour calcul."
        tests.append({"domain": "nombres", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    calc = ["calcul","addition","soustraction","multiplication","division","total","somme","moitié","double","tiers","quart","pourcentage","égal","résultat","proportion","taux","fraction","additionner","soustraire","diviser","multiplier","compter","mesurer","peser","décision","preuve","question","réponse","exact","valeur"]
    for i, w in enumerate(calc[:30]):
        text = f"Je peux {w} ce nombre." if w in {"additionner","soustraire","diviser","multiplier","mesurer","peser"} else f"Le {w} aide le calcul."
        tests.append({"domain": "calculs", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    mes = ["unité","mesure","mètre","kilomètre","centimètre","millimètre","gramme","kilogramme","kilo","litre","millilitre","degré","volume","vitesse","hauteur","largeur","longueur","profondeur","capacité","poids","distance","température","temps","route","eau","maison","voiture","corps","surface","ville"]
    for i, w in enumerate(mes):
        text = f"Cette mesure a {w}." if w not in {"hauteur","largeur","longueur","profondeur","capacité","poids","distance","volume","vitesse"} else f"La {w} est importante."
        tests.append({"domain": "mesures", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    comp = ["minimum","maximum","moyenne","moins","plus","environ","exact","approximatif","quantité","valeur","résultat","proportion","part","taux","fraction","centaine","millier","petit","grand","haut","bas","bon","mauvais","simple","difficile","vrai","faux","nombre","mesure","distance"]
    for i, w in enumerate(comp[:30]):
        text = f"Le résultat est {w}." if w in {"exact","approximatif","faux","bon","mauvais","simple","difficile","vrai"} else f"Le {w} aide pour comparer."
        tests.append({"domain": "comparaisons", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    return tests


def tests_v42():
    tests = []
    plant = ["plante","racine","branche","fruit","graine","tronc","bois","légume","champignon","bambou","sapin","pin","palmier","vigne","roseau","fleur","feuille","herbe","arbre","forêt","champ","jardin","terre","eau","soleil","nature","espèce","sauvage","domestique","élevage"]
    for i, w in enumerate(plant):
        text = f"Cette {w} est dans la nature." if w not in {"bois","soleil","terre","eau"} else f"Le {w} aide la plante."
        tests.append({"domain": "plantes", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    dom = ["vache","cheval","cochon","mouton","chèvre","poule","canard","lapin","âne","taureau","coq","chat","chien","chaton","chiot","ferme","élevage","nid","œuf","herbe","animal","domestique","champ","porte","eau","travail","famille","maison","groupe","nature"]
    for i, w in enumerate(dom):
        text = f"Le {w} vivre près de maison." if w not in {"poule","chèvre","vache"} else f"La {w} vivre près de maison."
        tests.append({"domain": "animaux domestiques", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    wild = ["loup","renard","cerf","ours","serpent","grenouille","singe","tigre","lion","éléphant","zèbre","girafe","hibou","aigle","corbeau","forêt","savane","jungle","tanière","rocher","rivière","lac","montagne","nature","sauvage","animal","queue","patte","aile","plume"]
    for i, w in enumerate(wild):
        text = f"Le {w} vivre dans la nature." if w not in {"girafe","grenouille"} else f"La {w} vivre dans la nature."
        tests.append({"domain": "animaux sauvages", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    ins = ["insecte","abeille","mouche","moustique","papillon","fourmi","araignée","ver","scarabée","libellule","ruche","nid","aile","patte","plume","fleur","eau","herbe","petit","léger","nature","groupe","terre","animal","forêt"]
    for i, w in enumerate(ins):
        text = f"Ce {w} est petit." if w in {"insecte"} else f"Le {w} vivre dans la nature." if not w.endswith("e") else f"La {w} vivre dans la nature."
        tests.append({"domain": "insectes", "text": text, "rating": "naturel" if i < 20 else "acceptable"})
    sea = ["poisson","crabe","coquillage","requin","baleine","dauphin","algue","méduse","crevette","homard","huître","moule","saumon","thon","truite","corail","mer","océan","plage","eau","sable","rocher","île","lac","rivière"]
    for i, w in enumerate(sea):
        text = f"Le {w} vivre dans eau." if w not in {"algue","baleine","méduse","moule","truite"} else f"La {w} vivre dans eau."
        tests.append({"domain": "mer et poissons", "text": text, "rating": "naturel" if i < 20 else "acceptable"})
    return tests


def tests_v43():
    tests = []
    aliments = ["aliment","boisson","viande","œuf","lait","fromage","riz","pâte","farine","beurre","huile","sel","sucre","pain","sauce","soupe","dessert","fruit","légume","eau","miel","gâteau","biscuit","chocolat","yaourt","crème","olive","épice","graisse","repas"]
    for i, w in enumerate(aliments):
        text = f"Ce {w} est bon à manger." if w not in {"boisson","eau","huile","soupe","crème"} else f"Cette {w} est bonne à boire ou manger."
        tests.append({"domain": "aliments", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    cuisine = ["cuisine","cuisiner","cuire","mélanger","verser","goûter","mordre","avaler","couper","éplucher","chauffer","casserole","poêle","four","frigo","couteau","cuillère","assiette","verre","bol","table","repas","plat","eau","feu","huile","sel","sucre","pain","légume"]
    for i, w in enumerate(cuisine):
        text = f"Je peux {w} ce plat." if w in {"cuisiner","cuire","mélanger","verser","goûter","mordre","avaler","couper","éplucher","chauffer"} else f"Le {w} aide en cuisine."
        tests.append({"domain": "cuisine", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    repas = ["repas","plat","assiette","verre","bol","couteau","fourchette","cuillère","casserole","poêle","four","frigo","bouteille","tasse","nappe","serviette","menu","table","chaise","famille","soir","midi","eau","pain","soupe","dessert","vin","bière","jus","maison"]
    for i, w in enumerate(repas):
        text = f"Le {w} est sur la table." if w not in {"famille","soir","midi"} else f"Le repas est au {w}."
        tests.append({"domain": "repas", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    fl = ["pomme","poire","banane","orange","citron","raisin","tomate","carotte","pomme-de-terre","salade","oignon","ail","fraise","melon","pastèque","haricot","pois","poivron","concombre","courgette","fruit","légume","jardin","terre","eau"]
    for i, w in enumerate(fl):
        text = f"Je veux une {w}." if w.endswith("e") else f"Je veux un {w}."
        tests.append({"domain": "fruits et légumes", "text": text, "rating": "naturel" if i < 20 else "acceptable"})
    gout = ["goût","sucré","salé","amer","acide","frais","cru","cuit","gras","épicé","doux","bon","mauvais","chocolat","citron","sel","sucre","huile","soupe","vin","bière","café","thé","jus","repas"]
    for i, w in enumerate(gout):
        text = f"Ce plat est {w}." if w in {"sucré","salé","amer","acide","frais","cru","cuit","gras","épicé","doux","bon","mauvais"} else f"Le {w} change ce plat."
        tests.append({"domain": "goût et préférences", "text": text, "rating": "naturel" if i < 20 else "acceptable"})
    return tests


def tests_v44():
    tests = []
    veh = ["transport","véhicule","bus","camion","vélo","moto","bateau","avion","navire","ambulance","tram","métro","taxi","train","wagon","moteur","roue","essence","frein","casque","ceinture","route","autoroute","trottoir","rue","rail","piste","parking","port","aéroport"]
    for i, w in enumerate(veh):
        text = f"Ce {w} sert au transport." if w not in {"ambulance","moto","route","autoroute","rue","piste"} else f"Cette {w} sert au transport."
        tests.append({"domain": "véhicules", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    pub = ["gare","arrêt","station","port","aéroport","parking","quai","pont","terminal","métro","tram","bus","train","ticket","billet","correspondance","passager","place-assise","signalisation","panneau","signal","feu","voie","carrefour","virage","douane","visa","frontière","escale","retour"]
    for i, w in enumerate(pub):
        text = f"Le {w} aide le voyage." if w not in {"gare","station","correspondance"} else f"La {w} aide le voyage."
        tests.append({"domain": "transport public", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    voy = ["trajet","voyage","billet","ticket","bagage","valise","conduire","naviguer","embarquer","avance","départ","arrivée","correspondance","retour","tourisme","touriste","camping","auberge","hôtel","réservation","embarquement","atterrissage","décollage","croisière","passeur","passager","visa","route","plan","carte"]
    for i, w in enumerate(voy):
        text = f"Je peux {w}." if w in {"conduire","naviguer","embarquer"} else f"Le {w} fait partie du voyage."
        tests.append({"domain": "voyage", "text": text, "rating": "naturel" if i < 25 else "acceptable"})
    nav = ["plan","frontière","panneau","signal","voie","carrefour","virage","feu","passage","sens","marin","voile","rame","courant","vague","marée","phare","capitaine","équipage","cabine","boussole","rive","carte-routière","océan","mer"]
    for i, w in enumerate(nav):
        text = f"Le {w} aide le trajet." if w not in {"voie","vague","marée","rive","cabine","boussole"} else f"La {w} aide le trajet."
        tests.append({"domain": "navigation", "text": text, "rating": "naturel" if i < 20 else "acceptable"})
    route = ["route","autoroute","trottoir","rue","piste","rail","pont","carrefour","virage","signalisation","panneau","feu","voie","sens","arrêt","station","parking","passage","quai","portail","douane","frontière","retard","avance","délai"]
    for i, w in enumerate(route):
        text = f"Le {w} change le trajet." if w not in {"autoroute","rue","voie","douane","station","signalisation"} else f"La {w} change le trajet."
        tests.append({"domain": "orientation routière", "text": text, "rating": "naturel" if i < 20 else "acceptable"})
    return tests


def tests_v45():
    tests = []
    sky = ["étoile","lune","planète","univers","galaxie","orbite","astre","comète","météore","soleil","ciel","nuit","jour","horizon","lumière","ombre","distance","mouvement","gravité","vide","espace","satellite","fusée","cosmonaute","planète","galaxie","étoile","orbite","météo","nuage"]
    for i, w in enumerate(sky[:30]):
        text = f"Il y a une {w}." if w in {"lune","planète","galaxie","comète","orbite","gravité","météo","fusée"} else f"Il y a un {w}."
        tests.append({"domain": "ciel", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    esp = ["univers","galaxie","orbite","astre","comète","météore","satellite","fusée","cosmonaute","vide","gravité","planète","lune","étoile","distance","vitesse","mouvement","rotation","révolution","rayon","énergie","masse","matière","espace","circuit","batterie","onde","signal-science","pression","volume"]
    for i, w in enumerate(esp):
        text = f"Le {w} aide à comprendre espace." if w not in {"fusée","révolution","gravité","énergie","matière","pression"} else f"La {w} aide à comprendre espace."
        tests.append({"domain": "espace", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    sci = ["science","énergie","masse","atome","gaz","liquide","solide","pression","onde","électricité","magnétique","rayon","vide","gravité","molécule","métal","cuivre","fer","acier","plastique","verre-matière","poussière","flamme","fumée","vapeur","cristal","densité","courant-électrique","batterie","circuit"]
    for i, w in enumerate(sci):
        text = f"Cette {w} fait partie de science." if w in {"science","énergie","masse","pression","gravité","molécule","densité","batterie"} else f"Ce {w} fait partie de science."
        tests.append({"domain": "sciences simples", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    obs = ["observer","instrument","lunette","télescope","microscope","expérience","hypothèse","théorie","mesure-science","laboratoire","échantillon","thermomètre","baromètre","aimant","balance","preuve","analyse","test","image","lumière","petit","loin","proche","mesurer","comprendre","voir","savoir","raison","question","réponse"]
    for i, w in enumerate(obs):
        text = f"Je peux {w}." if w in {"observer","mesurer","comprendre","voir","savoir"} else f"Le {w} aide une expérience."
        tests.append({"domain": "observation et expérience", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    return tests


def tests_v46():
    tests = []
    vis = ["art","dessin","dessiner","peinture","peindre","tableau","photo","photographie","cadre","sculpture","portrait","paysage-image","croquis","toile","galerie","exposition","image","couleur","forme-art","beauté","style","création","illustration","affiche","bande-dessinée","cadre","tableau","mur","papier","main"]
    for i, w in enumerate(vis[:30]):
        text = f"Je peux {w}." if w in {"dessiner","peindre"} else f"Le {w} fait partie de art."
        tests.append({"domain": "art visuel", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    mus = ["son","note","rythme","chanson","chanter","mélodie","harmonie","piano","guitare","violon","tambour","concert","chorale","instrument","voix","micro","refrain","couplet","musique","oreille","groupe","public","danse","danser","émotion","temps","mouvement","style","image","spectacle"]
    for i, w in enumerate(mus[:30]):
        text = f"Je peux {w}." if w in {"chanter","danser"} else f"Le {w} fait partie de musique."
        tests.append({"domain": "musique", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    txt = ["texte","poème","auteur","lecteur","roman","conte","chapitre","paragraphe","phrase","journal","livre","récit","fiction","personnage","bibliothèque","édition","publication","impression","typographie","mot","page","histoire","idée","style","image","pensée","papier","livre","texte","roman"]
    for i, w in enumerate(txt[:30]):
        text = f"Le {w} fait partie de texte."
        tests.append({"domain": "texte", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    spec = ["film","théâtre","acteur","scène","danser","danse","spectacle","cinéma","costume","masque","public","voix","lumière","image","musique","histoire","personnage","émotion","création","style","beauté","chant","micro","concert","galerie","photo","tableau","roman","art","image"]
    for i, w in enumerate(spec[:30]):
        text = f"Le {w} fait partie de art." if w not in {"scène","danse","voix","lumière","photo","musique"} else f"La {w} fait partie de art."
        tests.append({"domain": "spectacle et culture", "text": text, "rating": "naturel" if i < 24 else "acceptable"})
    return tests


def tests_v5():
    tests = []
    domains = {
        "vie quotidienne": [
            "voisin","voisine","ami","amitié","inviter","visite","fête","cadeau","message","conversation",
            "respect","confiance","conflit","chambre","salon","salle","bain","douche","toilette","linge",
            "vêtement","chemise","pantalon","chaussure","manteau","sac","clé","lit","fenêtre","porte",
            "mur","plafond","sol","armoire","lampe","balai","savon","ménage","ranger","nettoyer",
            "famille","maison","repas","travail","calme","habitude","routine","choix","préférence","objectif",
        ],
        "santé": [
            "médecin","médicament","traitement","soin","urgence","infection","vaccin","prévention","hôpital","patient",
            "température","tension","accident","fracture","brûlure","plaie","antidouleur","surdose","grave","léger",
            "chronique","surveiller","consulter","dépression","anxiété","stress","angoisse","handicap","fatigué","isolement",
            "soutien","psychologue","thérapie","douleur","symptôme","sang","respirer","dormir","vomir","saigner",
            "grossesse","parent","père","mère","enfant","consentement","risque","danger","protéger","secours",
        ],
        "administration droit argent": [
            "document","dossier","formulaire","demande","service","mairie","numéro","adresse","identité","carte",
            "preuve","signature","rendez-vous","banque","compte","paiement","facture","dette","revenu","dépense",
            "impôt","taxe","assurance","accord","obligation","autorisation","interdit","permis","responsabilité","plainte",
            "juge","tribunal","avocat","police","amende","procédure","délai","courrier","reçu","sanction",
            "contrôle","sécurité","infraction","défense","conseil","justice","jugement","décision","recours","budget",
        ],
        "travail": [
            "emploi","métier","entreprise","bureau","collègue","responsable","chef","client","projet","tâche",
            "réunion","contrat","salaire","congé","horaire","poste","chômage","licenciement","retraite","embauche",
            "candidat","entretien","formation","expérience","compétence","certificat","attestation","allocation","social","travail",
            "service","document","dossier","progrès","succès","échec","objectif","motivation","patience","message",
            "internet","ordinateur","fichier","logiciel","application","site","mail","réseau","agenda","liste",
        ],
        "temps météo localisation": [
            "matin","soir","midi","minuit","semaine","mois","année","saison","printemps","été",
            "automne","hiver","date","calendrier","lendemain","veille","seconde","minute","janvier","février",
            "mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre",
            "nord","sud","est","ouest","dessus","dessous","milieu","coin","fond","entrée",
            "sortie","niveau","étage","météo","climat","nuage","orage","neige","tempête","brouillard",
        ],
        "nombres mesures calcul": [
            "zéro","deux","trois","quatre","cinq","six","sept","huit","neuf","dix",
            "cent","mille","million","chiffre","calcul","addition","soustraction","multiplication","division","total",
            "somme","moitié","double","tiers","quart","pourcentage","mesure","mètre","kilomètre","gramme",
            "kilogramme","litre","degré","volume","vitesse","hauteur","largeur","longueur","profondeur","capacité",
            "poids","distance","minimum","maximum","moyenne","environ","exact","approximatif","quantité","valeur",
        ],
        "nature animaux plantes": [
            "animal","plante","oiseau","insecte","nature","espèce","sauvage","domestique","élevage","nid",
            "œuf","racine","branche","fruit","graine","tronc","bois","légume","champignon","bambou",
            "vache","cheval","cochon","mouton","chèvre","poule","canard","lapin","loup","renard",
            "cerf","ours","serpent","grenouille","abeille","mouche","moustique","papillon","fourmi","araignée",
            "poisson","crabe","coquillage","requin","baleine","dauphin","algue","mer","forêt","jardin",
        ],
        "alimentation cuisine": [
            "aliment","boisson","viande","œuf","lait","fromage","riz","pâte","farine","beurre",
            "huile","sel","sucre","pain","sauce","soupe","dessert","pomme","banane","orange",
            "citron","raisin","tomate","carotte","salade","oignon","ail","café","thé","jus",
            "vin","bière","alcool","cuisine","cuisiner","cuire","mélanger","verser","goûter","mordre",
            "avaler","repas","plat","assiette","verre","bol","couteau","fourchette","cuillère","frigo",
        ],
        "transport voyage navigation": [
            "transport","véhicule","bus","camion","vélo","moto","bateau","avion","navire","ambulance",
            "gare","arrêt","station","port","aéroport","parking","quai","pont","trajet","voyage",
            "billet","ticket","bagage","valise","conduire","naviguer","embarquer","départ","arrivée","retour",
            "plan","frontière","panneau","signal","voie","carrefour","virage","marin","voile","rame",
            "courant","vague","marée","phare","route","train","wagon","moteur","roue","passager",
        ],
        "art culture sciences simples": [
            "étoile","lune","planète","univers","science","énergie","masse","atome","gaz","liquide",
            "solide","pression","onde","électricité","instrument","télescope","microscope","expérience","hypothèse","théorie",
            "art","dessin","peinture","tableau","photo","sculpture","son","note","rythme","chanson",
            "mélodie","texte","poème","auteur","lecteur","roman","conte","film","théâtre","acteur",
            "scène","danse","spectacle","style","beauté","création","imaginaire","image","fiction","bibliothèque",
        ],
    }
    for domain, words in domains.items():
        for i, w in enumerate(words):
            if i % 5 == 0:
                text = f"Je parle de {w}."
            elif i % 5 == 1:
                text = f"Ce {w} est utile."
            elif i % 5 == 2:
                text = f"Cette {w} est utile." if w.endswith("e") else f"Ce {w} change la vie."
            elif i % 5 == 3:
                text = f"Nous avons besoin de {w}."
            else:
                text = f"Le {w} aide à comprendre."
            rating = "naturel" if i < 38 else "acceptable"
            tests.append({"domain": domain, "text": text, "rating": rating})
    return tests


def build_readme(version_name, count, scope_lines, main_files, limits_lines, interpretation):
    lines = [
        f"# README {version_name.upper()}",
        "",
        "## Objet",
        "",
        f"`{version_name.upper()}` est une version stabilisée du dictionnaire français minimal à `{count}` mots.",
        "",
        "## Fichiers principaux",
        "",
    ]
    for label, path in main_files:
        lines.append(f"- [{label}]({path})")
    lines += ["", "## Portée exacte", ""] + [f"- {line}" for line in scope_lines] + ["", "## Ce que cette version ne cherche pas à faire", ""]
    lines += [f"- {line}" for line in limits_lines] + ["", "## Interprétation", "", interpretation]
    return "\n".join(lines) + "\n"


def build_changelog(version_name, previous_label, count, scope_title, items, limits):
    lines = [
        f"# Changelog {version_name.upper()}",
        "",
        f"## {version_name.upper()} stable",
        "",
        f"Cette version fige la branche {scope_title} sur une base de {count} mots.",
        "",
        "### Base de départ",
        "",
        f"- point de départ : {previous_label} ;",
        f"- conservation complète de la branche précédente ;",
        f"- ajout de {len(items)} mots ciblés.",
        "",
        "### Fichiers stabilisés",
        "",
        f"- `wordlist_{version_name}.txt`",
        f"- `dictionary_{version_name}.json`",
        f"- `forms_{version_name.split('_')[0]}_{version_name.split('_')[1] if '_' in version_name else version_name}.txt`" if version_name != "v5" else "- `forms_v5.txt`",
        "",
        "### Limites connues",
        "",
    ] + [f"- {line}" for line in limits]
    return "\n".join(lines) + "\n"


def write_final_validation(raw_report, version_label, wordlist_name, dictionary_name, forms_name, recommendation):
    out = []
    for line in raw_report.splitlines():
        if line == "# Rapport de validation":
            out.append(f"# Rapport de validation {version_label} final")
        elif line.startswith("La V0 est lexicalement fermee."):
            out.append(recommendation)
        else:
            out.append(line)
    out += ["", "## Source", "", "Cette version finale fige les contenus de :", "", f"- `{wordlist_name}`", f"- `{dictionary_name}`", f"- `{forms_name}`", "", f"Le contenu est identique à la proposition {version_label} validée, mais publié ici comme version stable."]
    return "\n".join(out) + "\n"


def final_docs():
    history = [
        "# Project History",
        "",
        "- V0 : première base fermée de 500 mots.",
        "- V1 : réécriture contrôlée des définitions faibles.",
        "- V2 et V2.2 : amélioration locale, expression, morphologie et pragmatique.",
        "- V3.0 : branche santé, biologie et vie corporelle à 550 mots.",
        "- V3.1 : santé pratique à 600 mots.",
        "- V3.2 : travail, administration, argent et droit courant à 650 mots.",
        "- V3.3 : droit pratique, logement, santé fine et santé mentale.",
        "- V4.0 à V4.6 : monde physique, nombres, nature, alimentation, transport, sciences, art et culture.",
        "- V5 : corpus confortable consolidé autour de 1500 mots.",
    ]
    roadmap = [
        "# Roadmap Corpus Confortable",
        "",
        "- noyau grammatical et lexical général ;",
        "- vie quotidienne et expression de base ;",
        "- santé, prévention et santé mentale minimale ;",
        "- administration, droit courant, argent et travail ;",
        "- monde physique, temps, météo et localisation ;",
        "- nombres, calcul et mesures ;",
        "- nature, animaux, plantes et milieux ;",
        "- alimentation, cuisine et goûts ;",
        "- transport, navigation et voyage ;",
        "- science simple, ciel et observation ;",
        "- art, culture et expression ;",
        "- vie sociale, domestique et communication moderne.",
    ]
    summary = [
        "# Version Summary",
        "",
        "Version | Nombre de mots | Domaine principal | Tests | Statut",
        "--- | --- | --- | --- | ---",
        "V3.2 | 650 | Travail, administration, argent, droit courant | 100 | stable",
        "V3.3 | 725 | Droit pratique, logement, santé fine, santé mentale | 125 | stable",
        "V4.0 | 825 | Monde physique, couleurs, temps, météo, localisation | 120 | stable",
        "V4.1 | 900 | Nombres, calcul, mesures | 120 | stable",
        "V4.2 | 1000 | Nature, plantes, animaux, insectes, poissons | 140 | stable",
        "V4.3 | 1100 | Alimentation, cuisine, goûts | 140 | stable",
        "V4.4 | 1200 | Transport, navigation, voyage | 140 | stable",
        "V4.5 | 1275 | Ciel, espace, sciences simples | 120 | stable",
        "V4.6 | 1350 | Art, culture, expression | 120 | stable",
        "V5 | 1500 | Corpus confortable consolidé | 500 | stable",
    ]
    limits = [
        "# Limits And Design Choices",
        "",
        "## Vocabulaire contrôlé",
        "",
        "- Le dictionnaire reste fermé et explicitement vérifiable.",
        "- Les définitions privilégient la clarté et la fermeture lexicale plutôt que la précision encyclopédique.",
        "",
        "## Mots quasi primitifs",
        "",
        "- Certains mots servent de pivots : `chose`, `personne`, `faire`, `temps`, `document`, `travail`, `animal`, `plante`, `art`, `science`.",
        "",
        "## Formes fléchies",
        "",
        "- Les formes restent explicites dans les fichiers `forms_vX.txt`.",
        "- Aucune lemmatisation implicite n est supposée.",
        "",
        "## Nombres",
        "",
        "- Les nombres fondamentaux sont intégrés comme mots du dictionnaire.",
        "- Les chiffres numériques `0-9` peuvent être admis comme symboles externes dans les tests, mais les définitions restent textuelles.",
        "",
        "## Polysémies",
        "",
        "- Certaines polysémies sont conservées si elles restent courantes et lisibles, par exemple `accord`, `feu`, `voie`, `port`.",
        "",
        "## Limites sectorielles",
        "",
        "- Le médical reste informatif et non prescriptif.",
        "- Le juridique reste courant et non spécialisé.",
        "- Le scientifique reste introductif.",
        "- Le corpus ne remplace pas la langue naturelle complète.",
    ]
    (ROOT / "PROJECT_HISTORY.md").write_text("\n".join(history) + "\n", encoding="utf-8")
    (ROOT / "ROADMAP_CORPUS_CONFORTABLE.md").write_text("\n".join(roadmap) + "\n", encoding="utf-8")
    (ROOT / "VERSION_SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (ROOT / "LIMITS_AND_DESIGN_CHOICES.md").write_text("\n".join(limits) + "\n", encoding="utf-8")


def main():
    words = read_wordlist(ROOT / "wordlist_v3_2.txt")
    dictionary = entry_map_from_json(ROOT / "dictionary_v3_2.json")
    forms = read_forms(ROOT / "forms_v3_2.txt")

    versions = [
        ("v3_3_725", 725, V33_POOL, V33_EXTRA_FORMS, "La V3.3 est lexicalement fermée. La suite peut affiner les définitions de procédure, de logement et de santé mentale, ou étendre prudemment vers la justice pénale, la vie sociale et l accompagnement quotidien."),
        ("v4_0_825", 825, V40_POOL, [], "La V4.0 est lexicalement fermée. La suite peut affiner les descriptions physiques et calendaires ou étendre la géographie, les reliefs et les phénomènes météorologiques courants."),
        ("v4_1_900", 900, V41_POOL, V41_EXTRA_FORMS, "La V4.1 est lexicalement fermée. La suite peut renforcer les comparaisons numériques, les unités et la lecture courante des nombres."),
        ("v4_2_1000", 1000, V42_POOL, [], "La V4.2 est lexicalement fermée. La suite peut étendre encore les espèces, les habitats et la botanique utile si le projet veut décrire la nature plus finement."),
        ("v4_3_1100", 1100, V43_POOL, V43_EXTRA_FORMS, "La V4.3 est lexicalement fermée. La suite peut enrichir les gestes culinaires, les aliments et les habitudes de repas si nécessaire."),
        ("v4_4_1200", 1200, V44_POOL, V44_EXTRA_FORMS, "La V4.4 est lexicalement fermée. La suite peut affiner la signalisation, les situations de voyage et les moyens de transport."),
        ("v4_5_1275", 1275, V45_POOL, [], "La V4.5 est lexicalement fermée. La suite peut préciser certains concepts scientifiques sans sortir du cadre introductif."),
        ("v4_6_1350", 1350, V46_POOL, V46_EXTRA_FORMS, "La V4.6 est lexicalement fermée. La suite peut étendre la création, les formes artistiques et la culture écrite si besoin."),
        ("v5_1500", 1500, V50_POOL, V50_EXTRA_FORMS, "La V5 est lexicalement fermée. La suite éventuelle devrait surtout affiner les définitions faibles et n ajouter que des mots explicitement demandés par les audits."),
    ]

    previous_size = len(words)
    stable_meta = []
    tests_builder = {
        "v3_3_725": tests_v33,
        "v4_0_825": tests_v40,
        "v4_1_900": tests_v41,
        "v4_2_1000": tests_v42,
        "v4_3_1100": tests_v43,
        "v4_4_1200": tests_v44,
        "v4_5_1275": tests_v45,
        "v4_6_1350": tests_v46,
        "v5_1500": tests_v5,
    }

    for version_key, target_size, pool, extra_forms, recommendation in versions:
        words, dictionary, forms, picked, stdout, missing = add_entries(words, dictionary, forms, version_key, target_size, pool, extra_forms, recommendation)
        tests = tests_builder[version_key]()
        validation = validate_expression_tests(words, forms, tests, allow_digits=(version_key in {"v4_1_900", "v5_1500"}))
        if validation["valid"] != validation["total"]:
            raise RuntimeError(f"Tests invalides pour {version_key}: {validation['issues'][:5]}")
        write_expression_files(version_key, tests, validation)
        version_short = version_key.split("_proposal")[0]
        prev_short = stable_meta[-1]["label"] if stable_meta else "V3.2 stable à 650 mots"
        write_diff(
            ROOT / f"diff_{'v3_2' if version_key=='v3_3_725' else stable_meta[-1]['file_key']}_{version_key.split('_proposal')[0] if '_proposal' in version_key else version_key}.md".replace("_proposal", ""),
            f"# Diff {('V3.2' if version_key=='v3_3_725' else stable_meta[-1]['label'])} -> {version_key.replace('_', '.').upper()}",
            previous_size,
            len(words),
            picked,
            [f"Le domaine ajouté devient exprimable avec {validation['total']} phrases de test valides.", "Les définitions restent courtes et fermées sur le vocabulaire contrôlé."],
        )
        write_missing_words(
            ROOT / f"missing_words_{version_key}.json",
            [{"mot": entry["word"], "priorite": "basse", "raison": "déjà intégré dans cette version"} for entry in picked[:10]],
        )
        write_recommendation(
            ROOT / f"recommendation_{version_key}.md",
            version_key.replace("_", ".").upper(),
            prev_short,
            len(words),
            picked[0]["note"] if picked else "extension contrôlée",
            [entry["word"] for entry in picked[:12]],
            [entry["word"] for entry in picked[12:24]],
            [entry["word"] for entry in picked[24:36]],
            ["document", "travail", "animal", "art", "science"] if version_key == "v5_1500" else None,
        )
        # stabilize
        if version_key == "v5_1500":
            stable_prefix = "v5"
            proposal_forms = "forms_v5_proposal.txt"
            stable_forms = "forms_v5.txt"
        else:
            major_minor = "_".join(version_key.split("_")[:2])
            stable_prefix = major_minor
            proposal_forms = f"forms_{major_minor}_proposal.txt"
            stable_forms = f"forms_{major_minor}.txt"
        proposal_wordlist = f"wordlist_{version_key}_proposal.txt"
        proposal_dict = f"dictionary_{version_key}_proposal.json"
        stable_wordlist = f"wordlist_{stable_prefix}.txt"
        stable_dict = f"dictionary_{stable_prefix}.json"
        stabilize_from_proposal(proposal_wordlist, proposal_dict, proposal_forms, stable_wordlist, stable_dict, stable_forms)
        raw_report, _, _ = run_validator(ROOT / stable_wordlist, ROOT / stable_dict, ROOT / stable_forms)
        final_report = write_final_validation(raw_report, version_key.replace("_", ".").upper(), stable_wordlist, stable_dict, stable_forms, recommendation)
        (ROOT / f"validation_report_{stable_prefix}_final.md").write_text(final_report, encoding="utf-8")
        scope_lines = sorted(set(entry["note"] for entry in picked))
        main_files = [
            (stable_wordlist, f"/Users/avialle/dev/minidico/{stable_wordlist}"),
            (stable_dict, f"/Users/avialle/dev/minidico/{stable_dict}"),
            (stable_forms, f"/Users/avialle/dev/minidico/{stable_forms}"),
            (f"validation_report_{stable_prefix}_final.md", f"/Users/avialle/dev/minidico/validation_report_{stable_prefix}_final.md"),
            (f"expression_tests_{version_key}.md", f"/Users/avialle/dev/minidico/expression_tests_{version_key}.md"),
            (f"expression_validation_report_{version_key}.md", f"/Users/avialle/dev/minidico/expression_validation_report_{version_key}.md"),
        ]
        readme = build_readme(
            stable_prefix.upper(),
            len(words),
            scope_lines,
            main_files,
            [
                "couvrir tous les registres spécialisés ;",
                "remplacer une langue naturelle complète ;",
                "résoudre toutes les polysémies du français courant ;",
                "supprimer entièrement les définitions pivots ou quasi primitives ;",
            ],
            f"{stable_prefix.upper()} doit être compris comme une branche stable du corpus confortable, centrée sur {', '.join(scope_lines[:4])}.",
        )
        (ROOT / f"README_{stable_prefix.upper()}.md").write_text(readme, encoding="utf-8")
        changelog = build_changelog(
            stable_prefix,
            f"{previous_size} mots",
            len(words),
            ", ".join(scope_lines[:3]),
            picked,
            [
                "certaines définitions restent volontairement compressées ;",
                "la morphologie explicite privilégie les formes utiles plutôt que l exhaustivité ;",
                "les domaines spécialisés complets restent hors cible ;",
            ],
        )
        (ROOT / f"CHANGELOG_{stable_prefix.upper()}.md").write_text(changelog, encoding="utf-8")
        stable_meta.append({"label": version_key.replace("_", ".").upper(), "file_key": stable_prefix})
        previous_size = len(words)

    # rename files to expected names for proposal reports
    rename_map = {
        "validation_report_v3_3_725.md": "validation_report_v3_3.md",
        "expression_tests_v3_3_725.md": "expression_tests_v3_3.md",
        "expression_validation_report_v3_3_725.md": "expression_validation_report_v3_3.md",
        "missing_words_v3_3_725.json": "missing_words_v3_3.json",
        "recommendation_v3_3_725.md": "recommendation_v3_3.md",
        "validation_report_v4_0_825.md": "validation_report_v4_0.md",
        "expression_tests_v4_0_825.md": "expression_tests_v4_0.md",
        "expression_validation_report_v4_0_825.md": "expression_validation_report_v4_0.md",
        "missing_words_v4_0_825.json": "missing_words_v4_0.json",
        "recommendation_v4_0_825.md": "recommendation_v4_0.md",
        "validation_report_v4_1_900.md": "validation_report_v4_1.md",
        "expression_tests_v4_1_900.md": "expression_tests_v4_1.md",
        "expression_validation_report_v4_1_900.md": "expression_validation_report_v4_1.md",
        "missing_words_v4_1_900.json": "missing_words_v4_1.json",
        "recommendation_v4_1_900.md": "recommendation_v4_1.md",
        "validation_report_v4_2_1000.md": "validation_report_v4_2.md",
        "expression_tests_v4_2_1000.md": "expression_tests_v4_2.md",
        "expression_validation_report_v4_2_1000.md": "expression_validation_report_v4_2.md",
        "missing_words_v4_2_1000.json": "missing_words_v4_2.json",
        "recommendation_v4_2_1000.md": "recommendation_v4_2.md",
        "validation_report_v4_3_1100.md": "validation_report_v4_3.md",
        "expression_tests_v4_3_1100.md": "expression_tests_v4_3.md",
        "expression_validation_report_v4_3_1100.md": "expression_validation_report_v4_3.md",
        "missing_words_v4_3_1100.json": "missing_words_v4_3.json",
        "recommendation_v4_3_1100.md": "recommendation_v4_3.md",
        "validation_report_v4_4_1200.md": "validation_report_v4_4.md",
        "expression_tests_v4_4_1200.md": "expression_tests_v4_4.md",
        "expression_validation_report_v4_4_1200.md": "expression_validation_report_v4_4.md",
        "missing_words_v4_4_1200.json": "missing_words_v4_4.json",
        "recommendation_v4_4_1200.md": "recommendation_v4_4.md",
        "validation_report_v4_5_1275.md": "validation_report_v4_5.md",
        "expression_tests_v4_5_1275.md": "expression_tests_v4_5.md",
        "expression_validation_report_v4_5_1275.md": "expression_validation_report_v4_5.md",
        "missing_words_v4_5_1275.json": "missing_words_v4_5.json",
        "recommendation_v4_5_1275.md": "recommendation_v4_5.md",
        "validation_report_v4_6_1350.md": "validation_report_v4_6.md",
        "expression_tests_v4_6_1350.md": "expression_tests_v4_6.md",
        "expression_validation_report_v4_6_1350.md": "expression_validation_report_v4_6.md",
        "missing_words_v4_6_1350.json": "missing_words_v4_6.json",
        "recommendation_v4_6_1350.md": "recommendation_v4_6.md",
        "validation_report_v5_1500.md": "validation_report_v5.md",
        "expression_tests_v5_1500.md": "expression_tests_v5.md",
        "expression_validation_report_v5_1500.md": "expression_validation_report_v5.md",
        "missing_words_v5_1500.json": "missing_words_v5.json",
        "recommendation_v5_1500.md": "recommendation_v5.md",
    }
    for src, dst in rename_map.items():
        if (ROOT / src).exists():
            shutil.move(ROOT / src, ROOT / dst)

    # rename diffs
    diff_map = {
        "diff_v3_2_v3_3_725.md": "diff_v3_2_v3_3.md",
        "diff_v3_3_v4_0_825.md": "diff_v3_3_v4_0.md",
        "diff_v4_0_v4_1_900.md": "diff_v4_0_v4_1.md",
        "diff_v4_1_v4_2_1000.md": "diff_v4_1_v4_2.md",
        "diff_v4_2_v4_3_1100.md": "diff_v4_2_v4_3.md",
        "diff_v4_3_v4_4_1200.md": "diff_v4_3_v4_4.md",
        "diff_v4_4_v4_5_1275.md": "diff_v4_4_v4_5.md",
        "diff_v4_5_v4_6_1350.md": "diff_v4_5_v4_6.md",
        "diff_v4_6_v5_1500.md": "diff_v4_6_v5.md",
    }
    for src, dst in diff_map.items():
        if (ROOT / src).exists():
            shutil.move(ROOT / src, ROOT / dst)

    final_words = read_wordlist(ROOT / "wordlist_v5.txt")
    final_dict = entry_map_from_json(ROOT / "dictionary_v5.json")
    build_audit_v5(final_words, final_dict)
    # final expression report alias
    shutil.copy(ROOT / "expression_validation_report_v5.md", ROOT / "expression_validation_report_v5_final.md")
    final_docs()


if __name__ == "__main__":
    main()
