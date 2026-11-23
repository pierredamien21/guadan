// Contrôle écrit à la main pour l'alerte 1 : un littéral binaire commençant par 1 fait décaler
// (int)1 de 31 bits à muParserInt.cpp:186. Résultat le 2026-11-23 : aucun rapport UBSan, car ce
// décalage est défini en C++ (UBSan ne le signale qu'en C). L'alerte de cppcheck est fausse ici.
#include "muParserInt.h"
#include <iostream>

int main() {
    mu::ParserInt p;
    p.SetExpr(_T("#10000000000000000000000000000000"));
    std::cout << p.Eval() << "\n";
}
