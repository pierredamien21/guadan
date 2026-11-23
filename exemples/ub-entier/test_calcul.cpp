#include <climits>
#include <string>

int moyenne(int a, int b);

int main(int argc, char **argv) {
    std::string cas = argc > 1 ? argv[1] : "petits";
    if (cas == "grands")
        return moyenne(INT_MAX, INT_MAX - 2) == INT_MAX - 1 ? 0 : 1;
    return moyenne(2, 4) == 3 ? 0 : 1;
}
