#!/usr/bin/env bash
# Rejoue ARVO 25402 en natif (ARM64 ou x86-64) : extrait la preuve de concept de l'image ARVO
# sans la lancer, compile muparser avec ASan à la version vulnérable puis corrigée, et exige
# un rapport ASan sur la première et aucun sur la seconde.
# Usage : temoin_25402.sh <dossier_de_travail>   (prérequis : clang, cmake, docker, git)
set -euo pipefail
W="${1:?dossier de travail}"; ICI="$(cd "$(dirname "$0")" && pwd)"
FIX=322716256d60e316c9a3b905a387be36d4e47368
F="-fsanitize=address,undefined -fno-omit-frame-pointer -g"

mkdir -p "$W" && cd "$W"
if [ ! -s poc-25402 ]; then
  docker pull -q --platform linux/amd64 n132/arvo:25402-vul > /dev/null
  c=$(docker create --platform linux/amd64 n132/arvo:25402-vul) # créé, jamais lancé
  docker cp "$c:/tmp/poc" poc-25402; docker rm "$c" > /dev/null
fi
[ -d muparser ] || git clone -q https://github.com/beltoforion/muparser.git

essai() { # $1 = commit ; affiche oui/non selon la présence d'un rapport ASan
  git -C muparser checkout -q "$1"
  rm -rf muparser/build-san
  cmake -S muparser -B muparser/build-san -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang \
    -DCMAKE_BUILD_TYPE=Debug -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DENABLE_OPENMP=OFF \
    -DBUILD_SHARED_LIBS=OFF -DCMAKE_CXX_FLAGS="$F" > /dev/null
  cmake --build muparser/build-san -j"$(nproc)" > /dev/null
  clang++ $F -Imuparser/include "$ICI/declencheur_25402.cpp" muparser/build-san/libmuparser*.a -o temoin
  ASAN_OPTIONS=detect_leaks=0 ./temoin poc-25402 > "run-$1.log" 2>&1 || true
  grep -q "ERROR: AddressSanitizer" "run-$1.log" && echo oui || echo non
}

v=$(essai "$FIX^"); f=$(essai "$FIX")
echo "rapport ASan : vulnérable=$v corrigée=$f ($(uname -m))"
grep -m1 -A2 "ERROR: AddressSanitizer" "run-$FIX^.log" || true
[ "$v" = oui ] && [ "$f" = non ] && echo REPRODUIT || { echo "NON REPRODUIT"; exit 1; }
