// Harnais de fuzzing minimal pour muparser : une expression, SetExpr puis Eval, exceptions
// du parseur ignorées. Équivalent du set_eval_fuzzer.cc d'OSS-Fuzz, réécrit sans le recopier.
#include "muParser.h"
#include <cstddef>
#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    try {
        mu::Parser p;
        p.SetExpr(std::string(reinterpret_cast<const char *>(data), size));
        p.Eval();
    } catch (mu::Parser::exception_type &) {
    }
    return 0;
}
