#!/usr/bin/env bash
# Vérifie que l'image d'outils détecte réellement des défauts : ASan, UBSan, libFuzzer.
# Usage : verifier_image.sh [image]   (défaut : guadan-outils)
set -euo pipefail
IMAGE="${1:-guadan-outils}"
docker run --rm --network none "$IMAGE" bash -euo pipefail -c '
echo "arch: $(uname -m)"
clang --version | head -1; cmake --version | head -1; cppcheck --version
clang-tidy --version | grep -i version | head -1; ninja --version
cd /tmp
printf "#include <stdlib.h>\nint main(void){char*p=malloc(4);p[4]=1;free(p);return 0;}\n" > a.c
clang -g -fsanitize=address a.c -o a
! ./a 2>a.log; grep -q "heap-buffer-overflow" a.log || { echo "ASan : ÉCHEC"; exit 1; }; echo "ASan : ok"
printf "#include <limits.h>\nint main(int c,char**v){int x=INT_MAX;x+=c;return x==0;}\n" > u.c
clang -g -fsanitize=undefined -fno-sanitize-recover=all u.c -o u
! ./u 2>u.log; grep -q "signed integer overflow" u.log || { echo "UBSan : ÉCHEC"; exit 1; }; echo "UBSan : ok"
printf "#include <stdint.h>\n#include <stddef.h>\nint LLVMFuzzerTestOneInput(const uint8_t*d,size_t n){if(n>2&&d[0]==%s&&d[1]==%s&&d[2]==%s){volatile char b[2];b[n]=0;}return 0;}\n" "0x46" "0x55" "0x5a" > f.c
clang -g -fsanitize=fuzzer,address f.c -o f
./f -max_total_time=60 > f.log 2>&1 || true
grep -q "ERROR: AddressSanitizer" f.log || { echo "libFuzzer : ÉCHEC"; tail -5 f.log; exit 1; }; echo "libFuzzer : ok ($(grep -c "^#" f.log) lignes de progression)"
'
