#include "parseur.h"

int main() {
    const unsigned char m[] = {'M', 3, 'a', 'b', 'c'};
    return lire_message(m, sizeof m) == "abc" ? 0 : 1;
}
