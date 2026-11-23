// Témoin de l'étape 0 (ARVO 25402, muparser) : même logique que le fuzzer d'OSS-Fuzz
// set_eval_fuzzer.cc, mais lit l'entrée dans un fichier. Vérifie que la chaîne
// « compiler avec ASan, exécuter » détecte la faille en natif ARM64.
#include "muParser.h"
#include <fstream>
#include <iostream>
#include <sstream>

int main(int argc, char **argv) {
    if (argc != 2) { std::cerr << "usage: " << argv[0] << " <fichier_entree>\n"; return 2; }
    std::ifstream f(argv[1], std::ios::binary);
    std::stringstream ss;
    ss << f.rdbuf();
    try {
        mu::Parser p;
        p.SetExpr(ss.str());
        p.Eval();
    } catch (mu::Parser::exception_type &) {
        // une exception du parseur est un refus propre, pas une faille
    }
    return 0;
}
