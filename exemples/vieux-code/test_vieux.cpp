// Code d'avant C++17 : « register » est refusé par clang 18 en C++17 (corrigé par -Wno-register),
// et la variable inutilisée déclenche un avertissement que -Werror transforme en erreur.
int somme(int n) {
    register int s = 0;
    for (int i = 1; i <= n; ++i) s += i;
    return s;
}

int main() {
    int inutile = 0;
    return somme(4) == 10 ? 0 : 1;
}
