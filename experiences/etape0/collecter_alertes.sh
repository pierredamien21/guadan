#!/usr/bin/env bash
# Étape 0 : collecte les alertes de cppcheck et clang-tidy sur muparser, à la version vulnérable
# d'ARVO 25402 (parent du commit correctif), pour tester à la main si un modèle sait écrire
# un test déclencheur. Usage : collecter_alertes.sh <dossier_de_travail>
set -euo pipefail
W="${1:?dossier de travail}"
FIX=322716256d60e316c9a3b905a387be36d4e47368 # correctif d'ARVO 25402, heap-buffer-overflow READ 8

mkdir -p "$W" && cd "$W"
[ -d muparser ] || git clone -q https://github.com/beltoforion/muparser.git
cd muparser && git checkout -q "$FIX^" && echo "version : $(git rev-parse --short HEAD) (parent de ${FIX:0:9})"

# CMake 4 refuse les cmake_minimum_required < 3.5 de cette vieille version : contournement proposé par CMake
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 > ../cmake.log

cppcheck --project=build/compile_commands.json --enable=warning,performance,portability \
  --inline-suppr --quiet --template='{file}:{line}: [cppcheck/{id}] {message}' \
  2> ../cppcheck.txt || true

# shortcut: liste de contrôles réduite aux erreurs mémoire et logiques, à élargir à l'étape 1
run-clang-tidy -p build -quiet \
  -checks='-*,clang-analyzer-*,bugprone-*,-bugprone-easily-swappable-parameters' \
  'src/.*\.cpp' > ../clang-tidy.txt 2>/dev/null || true

cd ..
grep -E '^[^ ]+:[0-9]+: \[cppcheck' cppcheck.txt | sed "s#$PWD/muparser/##" > alertes.txt || true
grep -E '^[^ ]+:[0-9]+:[0-9]+: (warning|error):' clang-tidy.txt | sed "s#$PWD/muparser/##" | sort -u >> alertes.txt || true
echo "alertes : $(wc -l < alertes.txt) (cppcheck $(grep -c cppcheck alertes.txt || true))"
