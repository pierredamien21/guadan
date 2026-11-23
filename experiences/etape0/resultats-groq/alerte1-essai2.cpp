#include <iostream>
#include "muParserInt.h"

int main()
{
    try
    {
        mu::ParserInt parser;          // create the integer parser
        parser.SetExpr("#1");          // binary literal that triggers the UB shift
        std::cout << parser.Eval() << std::endl;
    }
    catch (const std::exception& e)     // catch any parser‑related exceptions
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}
