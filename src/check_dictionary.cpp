#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace {

struct Entry {
    std::string category;
    std::string definition;
    std::vector<std::string> examples;
    std::string note;
};

struct MissingInfo {
    int frequency = 0;
    std::set<std::string> used_in;
    std::string probable_category = "inconnu";
    std::string importance = "evitable";
    std::string suggestion = "rewrite";
    std::string justification;
};

struct JsonValue {
    enum class Type { Null, String, Array, Object };

    Type type = Type::Null;
    std::string string_value;
    std::vector<JsonValue> array_value;
    std::map<std::string, JsonValue> object_value;
};

class JsonParser {
public:
    explicit JsonParser(const std::string &input) : input_(input) {}

    JsonValue parse() {
        skip_ws();
        JsonValue value = parse_value();
        skip_ws();
        if (pos_ != input_.size()) {
            throw std::runtime_error("caracteres JSON en trop");
        }
        return value;
    }

private:
    JsonValue parse_value() {
        skip_ws();
        if (pos_ >= input_.size()) {
            throw std::runtime_error("fin de JSON inattendue");
        }
        const char c = input_[pos_];
        if (c == '"') {
            JsonValue value;
            value.type = JsonValue::Type::String;
            value.string_value = parse_string();
            return value;
        }
        if (c == '{') {
            return parse_object();
        }
        if (c == '[') {
            return parse_array();
        }
        if (input_.compare(pos_, 4, "null") == 0) {
            pos_ += 4;
            return JsonValue{};
        }
        throw std::runtime_error("valeur JSON non prise en charge");
    }

    JsonValue parse_object() {
        expect('{');
        JsonValue value;
        value.type = JsonValue::Type::Object;
        skip_ws();
        if (peek('}')) {
            expect('}');
            return value;
        }
        while (true) {
            skip_ws();
            std::string key = parse_string();
            skip_ws();
            expect(':');
            skip_ws();
            value.object_value.emplace(key, parse_value());
            skip_ws();
            if (peek('}')) {
                expect('}');
                break;
            }
            expect(',');
        }
        return value;
    }

    JsonValue parse_array() {
        expect('[');
        JsonValue value;
        value.type = JsonValue::Type::Array;
        skip_ws();
        if (peek(']')) {
            expect(']');
            return value;
        }
        while (true) {
            value.array_value.push_back(parse_value());
            skip_ws();
            if (peek(']')) {
                expect(']');
                break;
            }
            expect(',');
        }
        return value;
    }

    std::string parse_string() {
        expect('"');
        std::string out;
        while (pos_ < input_.size()) {
            char c = input_[pos_++];
            if (c == '"') {
                return out;
            }
            if (c == '\\') {
                if (pos_ >= input_.size()) {
                    throw std::runtime_error("echappement JSON incomplet");
                }
                char e = input_[pos_++];
                switch (e) {
                case '"':
                case '\\':
                case '/':
                    out.push_back(e);
                    break;
                case 'b':
                    out.push_back('\b');
                    break;
                case 'f':
                    out.push_back('\f');
                    break;
                case 'n':
                    out.push_back('\n');
                    break;
                case 'r':
                    out.push_back('\r');
                    break;
                case 't':
                    out.push_back('\t');
                    break;
                case 'u':
                    out += "\\u";
                    for (int i = 0; i < 4; ++i) {
                        if (pos_ >= input_.size()) {
                            throw std::runtime_error("echappement unicode incomplet");
                        }
                        out.push_back(input_[pos_++]);
                    }
                    break;
                default:
                    throw std::runtime_error("echappement JSON non pris en charge");
                }
            } else {
                out.push_back(c);
            }
        }
        throw std::runtime_error("chaine JSON non fermee");
    }

    void skip_ws() {
        while (pos_ < input_.size() &&
               (input_[pos_] == ' ' || input_[pos_] == '\n' || input_[pos_] == '\r' ||
                input_[pos_] == '\t')) {
            ++pos_;
        }
    }

    bool peek(char expected) const {
        return pos_ < input_.size() && input_[pos_] == expected;
    }

    void expect(char expected) {
        if (pos_ >= input_.size() || input_[pos_] != expected) {
            throw std::runtime_error("JSON mal forme");
        }
        ++pos_;
    }

    const std::string &input_;
    std::size_t pos_ = 0;
};

std::string read_file(const std::string &path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("impossible de lire " + path);
    }
    std::ostringstream buffer;
    buffer << in.rdbuf();
    return buffer.str();
}

std::string trim(const std::string &value) {
    std::size_t start = 0;
    while (start < value.size() && std::isspace(static_cast<unsigned char>(value[start]))) {
        ++start;
    }
    std::size_t end = value.size();
    while (end > start && std::isspace(static_cast<unsigned char>(value[end - 1]))) {
        --end;
    }
    return value.substr(start, end - start);
}

std::string normalize_text(std::string value) {
    for (char &c : value) {
        if (c == '\'') {
            c = static_cast<char>(0x27);
        }
    }
    return value;
}

bool is_token_byte(unsigned char c) {
    if (c >= 128) {
        return true;
    }
    return std::isalpha(c) || c == '\'' || c == '-' ;
}

std::string lowercase_ascii(std::string value) {
    for (char &c : value) {
        if (static_cast<unsigned char>(c) < 128) {
            c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        }
    }
    return value;
}

std::string normalize_token(std::string token) {
    token = lowercase_ascii(token);
    std::size_t pos = 0;
    while ((pos = token.find('\'', pos)) != std::string::npos) {
        token.replace(pos, 1, "’");
        pos += 3;
    }
    while (!token.empty() && token.front() == '-') {
        token.erase(token.begin());
    }
    while (!token.empty() && token.back() == '-') {
        token.pop_back();
    }
    while (token.rfind("’", 0) == 0) {
        token.erase(0, std::string("’").size());
    }
    while (token.size() >= std::string("’").size() &&
           token.compare(token.size() - std::string("’").size(), std::string("’").size(), "’") == 0) {
        token.erase(token.size() - std::string("’").size());
    }
    static const std::vector<std::string> elisions = {
        "l’", "d’", "j’", "qu’", "n’", "s’", "c’", "m’", "t’"
    };
    for (const auto &prefix : elisions) {
        if (token.rfind(prefix, 0) == 0 && token.size() > prefix.size()) {
            token = token.substr(prefix.size());
            break;
        }
    }
    return token;
}

std::vector<std::string> tokenize(const std::string &text) {
    std::vector<std::string> tokens;
    std::string current;
    for (unsigned char c : text) {
        if (is_token_byte(c)) {
            current.push_back(static_cast<char>(c));
        } else if (!current.empty()) {
            std::string token = normalize_token(current);
            if (!token.empty()) {
                tokens.push_back(token);
            }
            current.clear();
        }
    }
    if (!current.empty()) {
        std::string token = normalize_token(current);
        if (!token.empty()) {
            tokens.push_back(token);
        }
    }
    return tokens;
}

std::vector<std::string> read_wordlist(const std::string &path,
                                       std::vector<std::string> &duplicates) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("impossible de lire " + path);
    }
    std::vector<std::string> words;
    std::unordered_set<std::string> seen;
    std::string line;
    while (std::getline(in, line)) {
        line = trim(line);
        if (line.empty()) {
            continue;
        }
        line = normalize_token(line);
        if (!seen.insert(line).second) {
            duplicates.push_back(line);
        }
        words.push_back(line);
    }
    return words;
}

std::unordered_map<std::string, std::string> read_forms(const std::string &path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("impossible de lire " + path);
    }
    std::unordered_map<std::string, std::string> forms;
    std::string line;
    while (std::getline(in, line)) {
        line = trim(line);
        if (line.empty()) {
            continue;
        }
        std::istringstream iss(line);
        std::string form;
        std::string lemma;
        if (!(iss >> form >> lemma)) {
            throw std::runtime_error("ligne invalide dans forms.txt: " + line);
        }
        forms[normalize_token(form)] = normalize_token(lemma);
    }
    return forms;
}

std::map<std::string, Entry> read_dictionary(const std::string &path) {
    JsonParser parser(read_file(path));
    JsonValue root = parser.parse();
    if (root.type != JsonValue::Type::Object) {
        throw std::runtime_error("dictionary.json doit contenir un objet");
    }

    std::map<std::string, Entry> dictionary;
    for (const auto &pair : root.object_value) {
        if (pair.second.type != JsonValue::Type::Object) {
            throw std::runtime_error("entree de dictionnaire invalide pour " + pair.first);
        }
        Entry entry;
        const auto &obj = pair.second.object_value;
        auto cat_it = obj.find("categorie");
        auto def_it = obj.find("definition");
        auto ex_it = obj.find("exemples");
        auto note_it = obj.find("note");
        if (cat_it == obj.end() || cat_it->second.type != JsonValue::Type::String) {
            throw std::runtime_error("categorie manquante pour " + pair.first);
        }
        if (def_it == obj.end() || def_it->second.type != JsonValue::Type::String) {
            throw std::runtime_error("definition manquante pour " + pair.first);
        }
        entry.category = cat_it->second.string_value;
        entry.definition = def_it->second.string_value;
        if (ex_it != obj.end()) {
            if (ex_it->second.type != JsonValue::Type::Array) {
                throw std::runtime_error("exemples invalide pour " + pair.first);
            }
            for (const auto &item : ex_it->second.array_value) {
                if (item.type != JsonValue::Type::String) {
                    throw std::runtime_error("exemple non texte pour " + pair.first);
                }
                entry.examples.push_back(item.string_value);
            }
        }
        if (note_it != obj.end() && note_it->second.type == JsonValue::Type::String) {
            entry.note = note_it->second.string_value;
        }
        dictionary[normalize_token(pair.first)] = entry;
    }
    return dictionary;
}

std::string guess_category(const std::string &token) {
    static const std::unordered_set<std::string> grammar = {
        "le", "la", "les", "de", "à", "et", "ou", "mais", "si", "pour", "dans",
        "sur", "sous", "avec", "sans", "qui", "que", "où", "ne", "pas"
    };
    if (grammar.count(token) > 0) {
        return "grammaire";
    }
    if (token.size() >= 2 &&
        (token.compare(token.size() - 2, 2, "er") == 0 ||
         token.compare(token.size() - 2, 2, "ir") == 0 ||
         token.compare(token.size() - 2, 2, "re") == 0)) {
        return "verbe";
    }
    if (token.size() >= 3 &&
        (token.compare(token.size() - 3, 3, "eux") == 0 ||
         token.compare(token.size() - 2, 2, "if") == 0 ||
         token.compare(token.size() - 3, 3, "ive") == 0)) {
        return "adjectif";
    }
    return "nom";
}

std::string decide_importance(const MissingInfo &info) {
    if (info.frequency >= 5 || info.used_in.size() >= 5) {
        return "essentiel";
    }
    if (info.frequency >= 3 || info.used_in.size() >= 3) {
        return "utile";
    }
    if (info.frequency == 1 && info.used_in.size() == 1) {
        return "evitable";
    }
    return "bruit";
}

std::string json_escape(const std::string &value) {
    std::string out;
    for (char c : value) {
        switch (c) {
        case '\\':
            out += "\\\\";
            break;
        case '"':
            out += "\\\"";
            break;
        case '\n':
            out += "\\n";
            break;
        default:
            out.push_back(c);
            break;
        }
    }
    return out;
}

} // namespace

int main() {
    try {
        std::vector<std::string> duplicate_wordlist;
        std::vector<std::string> wordlist = read_wordlist("wordlist.txt", duplicate_wordlist);
        std::unordered_set<std::string> allowed(wordlist.begin(), wordlist.end());
        std::unordered_map<std::string, std::string> forms = read_forms("forms.txt");
        std::map<std::string, Entry> dictionary = read_dictionary("dictionary.json");

        std::vector<std::string> dictionary_not_in_wordlist;
        std::vector<std::string> wordlist_not_in_dictionary;
        std::vector<std::string> empty_definitions;
        std::vector<std::string> missing_category;
        std::vector<std::string> circularities;
        std::vector<std::string> apostrophe_issues;

        std::map<std::string, MissingInfo> missing;
        std::map<std::string, std::set<std::string>> graph;
        std::map<std::string, int> inbound;

        for (const auto &pair : dictionary) {
            if (allowed.count(pair.first) == 0) {
                dictionary_not_in_wordlist.push_back(pair.first);
            }
        }
        for (const auto &word : wordlist) {
            if (dictionary.count(word) == 0) {
                wordlist_not_in_dictionary.push_back(word);
            }
        }

        int conformant_definitions = 0;
        for (const auto &pair : dictionary) {
            const std::string &word = pair.first;
            const Entry &entry = pair.second;
            if (trim(entry.category).empty()) {
                missing_category.push_back(word);
            }
            if (trim(entry.definition).empty()) {
                empty_definitions.push_back(word);
                continue;
            }

            const std::string definition = normalize_text(entry.definition);
            if (definition.find("''") != std::string::npos || definition.find("’’") != std::string::npos) {
                apostrophe_issues.push_back(word);
            }

            bool definition_ok = true;
            std::vector<std::string> tokens = tokenize(definition);
            for (const std::string &token : tokens) {
                std::string lemma = token;
                auto form_it = forms.find(token);
                if (form_it != forms.end()) {
                    lemma = form_it->second;
                }
                if (lemma == word) {
                    circularities.push_back(word);
                }
                if (allowed.count(lemma) == 0) {
                    definition_ok = false;
                    MissingInfo &info = missing[token];
                    info.frequency += 1;
                    info.used_in.insert(word);
                    info.probable_category = guess_category(token);
                } else if (lemma != word && dictionary.count(lemma) > 0) {
                    graph[word].insert(lemma);
                    inbound[lemma] += 1;
                }
            }
            if (definition_ok) {
                conformant_definitions += 1;
            }
        }

        std::vector<std::pair<std::string, MissingInfo>> missing_entries(missing.begin(), missing.end());
        std::sort(missing_entries.begin(), missing_entries.end(),
                  [](const auto &lhs, const auto &rhs) {
                      if (lhs.second.frequency != rhs.second.frequency) {
                          return lhs.second.frequency > rhs.second.frequency;
                      }
                      if (lhs.second.used_in.size() != rhs.second.used_in.size()) {
                          return lhs.second.used_in.size() > rhs.second.used_in.size();
                      }
                      return lhs.first < rhs.first;
                  });

        for (auto &item : missing_entries) {
            item.second.importance = decide_importance(item.second);
            item.second.suggestion =
                (item.second.importance == "essentiel" || item.second.importance == "utile") ? "add"
                                                                                            : "rewrite";
            if (item.second.used_in.empty()) {
                item.second.justification = "Mot isole, probablement evitable par reecriture.";
            } else if (item.second.used_in.size() >= 3) {
                item.second.justification =
                    "Ce mot revient dans plusieurs definitions fondamentales.";
            } else {
                item.second.justification =
                    "Ce mot apparait dans peu de definitions et peut souvent etre reecrit.";
            }
        }

        {
            std::ofstream out("missing_words.json");
            out << "{\n";
            for (std::size_t i = 0; i < missing_entries.size(); ++i) {
                const auto &item = missing_entries[i];
                out << "  \"" << json_escape(item.first) << "\": {\n";
                out << "    \"frequence\": " << item.second.frequency << ",\n";
                out << "    \"utilise_dans\": [";
                std::size_t index = 0;
                for (const auto &word : item.second.used_in) {
                    if (index++ > 0) {
                        out << ", ";
                    }
                    out << "\"" << json_escape(word) << "\"";
                }
                out << "],\n";
                out << "    \"categorie_probable\": \"" << item.second.probable_category << "\",\n";
                out << "    \"importance\": \"" << item.second.importance << "\",\n";
                out << "    \"suggestion\": \"" << item.second.suggestion << "\",\n";
                out << "    \"justification\": \"" << json_escape(item.second.justification) << "\"\n";
                out << "  }";
                if (i + 1 != missing_entries.size()) {
                    out << ",";
                }
                out << "\n";
            }
            out << "}\n";
        }

        {
            std::ofstream out("missing_words_report.md");
            out << "# Rapport des mots manquants\n\n";
            out << "- Nombre de mots hors vocabulaire: " << missing_entries.size() << "\n";
            if (missing_entries.empty()) {
                out << "- Aucun mot hors vocabulaire detecte dans les definitions de la V0.\n";
                out << "- Strategie A: aucune extension immediate du vocabulaire n'est necessaire.\n";
                out << "- Strategie B: conserver la reecriture minimale seulement si l'on veut enrichir le style.\n";
            } else {
                out << "\n| Mot | Frequence | Entrees | Importance | Suggestion |\n";
                out << "| --- | ---: | ---: | --- | --- |\n";
                for (const auto &item : missing_entries) {
                    out << "| " << item.first << " | " << item.second.frequency << " | "
                        << item.second.used_in.size() << " | " << item.second.importance << " | "
                        << item.second.suggestion << " |\n";
                }
            }
        }

        {
            std::vector<std::pair<std::string, int>> structured(inbound.begin(), inbound.end());
            std::sort(structured.begin(), structured.end(),
                      [](const auto &lhs, const auto &rhs) {
                          if (lhs.second != rhs.second) {
                              return lhs.second > rhs.second;
                          }
                          return lhs.first < rhs.first;
                      });

            std::ofstream out("validation_report.md");
            out << "# Rapport de validation\n\n";
            out << "- Mots dans `wordlist.txt`: " << wordlist.size() << "\n";
            out << "- Entrees dans `dictionary.json`: " << dictionary.size() << "\n";
            out << "- Definitions conformes: " << conformant_definitions << "\n";
            out << "- Mots hors vocabulaire: " << missing_entries.size() << "\n";
            out << "- Doublons dans la liste: " << duplicate_wordlist.size() << "\n";
            out << "- Mots de la liste sans entree: " << wordlist_not_in_dictionary.size() << "\n";
            out << "- Entrees hors liste: " << dictionary_not_in_wordlist.size() << "\n";
            out << "- Definitions vides: " << empty_definitions.size() << "\n";
            out << "- Categories manquantes: " << missing_category.size() << "\n";
            out << "- Circularites directes simples: " << circularities.size() << "\n";
            out << "- Problemes d'apostrophes: " << apostrophe_issues.size() << "\n";
            out << "\n## Recommandations\n\n";
            if (missing_entries.empty()) {
                out << "La V0 est lexicalement fermee. La prochaine iteration doit surtout enrichir la precision des definitions, pas agrandir la liste.\n";
            } else {
                out << "La V0 demande une reecriture ou une extension ciblee avant de passer a une V1.\n";
            }
            out << "\n## Mots structurants\n\n";
            std::size_t limit = std::min<std::size_t>(10, structured.size());
            if (limit == 0) {
                out << "Aucune dependance calculee.\n";
            } else {
                for (std::size_t i = 0; i < limit; ++i) {
                    out << "- " << structured[i].first << ": " << structured[i].second
                        << " definitions dependantes\n";
                }
            }
        }

        {
            std::ofstream out("definition_graph.dot");
            out << "digraph definitions {\n";
            out << "  rankdir=LR;\n";
            for (const auto &pair : graph) {
                for (const auto &target : pair.second) {
                    out << "  \"" << pair.first << "\" -> \"" << target << "\";\n";
                }
            }
            out << "}\n";
        }

        {
            std::ofstream out("stats.json");
            out << "{\n";
            out << "  \"word_count\": " << wordlist.size() << ",\n";
            out << "  \"dictionary_entries\": " << dictionary.size() << ",\n";
            out << "  \"conformant_definitions\": " << conformant_definitions << ",\n";
            out << "  \"missing_words\": " << missing_entries.size() << "\n";
            out << "}\n";
        }

        bool ok = duplicate_wordlist.empty() && dictionary_not_in_wordlist.empty() &&
                  wordlist_not_in_dictionary.empty() && empty_definitions.empty() &&
                  missing_entries.empty() && missing_category.empty();

        std::cout << "Validation terminee: " << (ok ? "OK" : "ECHEC") << "\n";
        std::cout << "Definitions conformes: " << conformant_definitions << "/"
                  << dictionary.size() << "\n";
        std::cout << "Mots hors vocabulaire: " << missing_entries.size() << "\n";
        return ok ? 0 : 1;
    } catch (const std::exception &ex) {
        std::cerr << "Erreur: " << ex.what() << "\n";
        return 2;
    }
}
