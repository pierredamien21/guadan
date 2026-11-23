#include <cstring>

// Copie une chaîne dans un tampon alloué. Défaut voulu : le chemin des chaînes longues oublie
// la place du zéro final.
char *copie(const char *s) {
    size_t n = std::strlen(s);
    char *t = new char[n < 16 ? n + 1 : n];
    std::memcpy(t, s, n + 1); // DEFAUT : n + 1 octets écrits dans un tampon de n si n >= 16
    return t;
}
