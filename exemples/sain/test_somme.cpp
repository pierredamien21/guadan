#include <cassert>
#include <vector>

static int somme(const std::vector<int> &v) {
    int s = 0;
    for (int x : v) s += x;
    return s;
}

int main() {
    assert(somme({1, 2, 3}) == 6);
    assert(somme({}) == 0);
    return 0;
}
