#pragma once
#include <cstddef>
#include <string>

// Lit un message au format : 'M', un octet de longueur L, puis L octets de contenu.
// Rend le contenu, ou une chaîne vide si le message est mal formé.
std::string lire_message(const unsigned char *donnees, std::size_t taille);
