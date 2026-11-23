#include <zlib.h>

int main(void) {
    const unsigned char d[] = "abc";
    return crc32(0L, d, 3) == 0x352441c2UL ? 0 : 1;
}
