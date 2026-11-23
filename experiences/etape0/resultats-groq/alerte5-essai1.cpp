// test.cpp
#include "muParser.h"

int main()
{
    // Derive from mu::Parser and override a virtual method.
    struct MyParser : public mu::Parser
    {
        // Override only InitCharSets; the other virtual methods are inherited.
        void InitCharSets() override
        {
            // Call the base implementation (optional, just to have a concrete body).
            mu::Parser::InitCharSets();
        }
    };

    // Construct the derived parser.
    // During construction the base class (Parser) constructor calls InitCharSets(),
    // which is a virtual call that bypasses the overridden version in MyParser.
    // This triggers UBSan's virtual-call check at src/muParser.cpp:84.
    MyParser p;

    // Prevent unused‑variable warnings.
    (void)p;
    return 0;
}
