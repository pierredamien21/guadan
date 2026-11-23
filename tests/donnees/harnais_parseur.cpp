// Harnais écrit à la main pour parseur-fragile : sert à tester le fuzzing sans LLM.
#include "parseur.h"

#include <cstddef>
#include <cstdint>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *d, size_t n) {
    lire_message(d, n);
    return 0;
}
