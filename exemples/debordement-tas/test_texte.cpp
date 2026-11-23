#include <cstring>
#include <string>

char *copie(const char *s);

int main(int argc, char **argv) {
    std::string cas = argc > 1 ? argv[1] : "courte";
    const char *source = cas == "longue" ? "une chaine assez longue" : "";
    char *c = copie(source);
    bool ok = std::strcmp(c, source) == 0;
    delete[] c;
    return ok ? 0 : 1;
}
