#!/usr/bin/env bash
# Étape 0 : le fuzzing retrouve-t-il seul la faille ARVO 25402, sans preuve de concept fournie ?
# Le harnais (fuzz_harnais.cpp) est le genre de programme qu'un modèle sait écrire : il appelle
# l'API publique. libFuzzer cherche l'entrée, ASan prouve. Usage : fuzz_25402.sh <travail> [secondes]
set -euo pipefail
W="${1:?dossier de travail}"; DUREE="${2:-300}"; ICI="$(cd "$(dirname "$0")" && pwd)"
FIX=322716256d60e316c9a3b905a387be36d4e47368
cd "$W"; [ -d muparser ] || git clone -q https://github.com/beltoforion/muparser.git
git -C muparser checkout -q "$FIX^"
B=muparser/build-fuzz
if [ ! -f "$B/libmuparser.a" ]; then
  cmake -S muparser -B "$B" -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang \
    -DCMAKE_BUILD_TYPE=Debug -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DENABLE_OPENMP=OFF \
    -DBUILD_SHARED_LIBS=OFF -DCMAKE_CXX_FLAGS="-fsanitize=fuzzer-no-link,address -g" > /dev/null
  cmake --build "$B" -j"$(nproc)" > /dev/null
fi
clang++ -fsanitize=fuzzer,address -g -Imuparser/include "$ICI/fuzz_harnais.cpp" "$B/libmuparser.a" -o fuzzer
rm -rf corpus crash-*; mkdir corpus; [ -d "$ICI/fuzz_graines" ] && cp "$ICI"/fuzz_graines/* corpus/
ASAN_OPTIONS=detect_leaks=0 ./fuzzer corpus -max_total_time="$DUREE" -max_len=512 \
  -print_final_stats=1 ${DICT:+-dict="$ICI/fuzz.dict"} > fuzz.log 2>&1 || true
grep -m1 -A3 "ERROR: AddressSanitizer" fuzz.log || echo "aucun rapport ASan en $DUREE s"
grep -E "stat::number_of_executed_units|Done [0-9]+ runs|Test unit written" fuzz.log || true
