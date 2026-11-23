// Défauts visibles par l'analyse statique, jamais exécutés : servent à tester guadan.
int dernier() {
    int t[3] = {1, 2, 3};
    return t[3]; // DEFAUT : indice hors limites (cppcheck arrayIndexOutOfBounds)
}

double moitie(int a) {
    return a / 2; // division entière dans un contexte flottant (bugprone-integer-division)
}
