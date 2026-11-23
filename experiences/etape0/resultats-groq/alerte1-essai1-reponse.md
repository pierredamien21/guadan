```cpp
#include <iostream>
#include "muParserInt.h"

int main()
{
    try
    {
        mu::ParserInt parser;          // create the integer parser
        parser.SetExpr("#1");          // binary literal that triggers the shift
        std::cout << parser.Eval() << std::endl;
    }
    catch (const mu::Parser::exception_type& e)
    {
        std::cerr << "Parser error: " << e.GetMsg() << std::endl;
        return 1;
    }
    return 0;
}
```