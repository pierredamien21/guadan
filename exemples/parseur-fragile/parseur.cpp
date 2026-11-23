#include "parseur.h"

#include <cstring>

std::string lire_message(const unsigned char *donnees, std::size_t taille) {
    if (taille < 2 || donnees[0] != 'M')
        return "";
    unsigned longueur = donnees[1];
    char tampon[32];
    if (longueur > taille - 2)
        return "";
    std::memcpy(tampon, donnees + 2, longueur); // DEFAUT : longueur peut dépasser 32
    return std::string(tampon, longueur < sizeof tampon ? longueur : sizeof tampon);
}
