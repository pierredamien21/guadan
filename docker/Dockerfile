# Image d'outils de guadan : tout ce qu'il faut pour compiler, tester et analyser un dépôt
# C/C++ CMake avec les sanitizers. Ubuntu 24.04 (clang 18, CMake 3.28) : voir D-12.
# shortcut: image de base désignée par étiquette, pas par empreinte ; à figer avant la publication (T17)
FROM ubuntu:24.04

ARG LLVM=18
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      clang-${LLVM} clang-tidy-${LLVM} clang-tools-${LLVM} libclang-rt-${LLVM}-dev llvm-${LLVM} \
      libomp-${LLVM}-dev \
      cmake ninja-build make pkg-config cppcheck git ca-certificates python3 \
 && rm -rf /var/lib/apt/lists/* \
 && for t in clang clang++ clang-tidy run-clang-tidy llvm-symbolizer; do \
      ln -sf "$(command -v $t-${LLVM})" /usr/local/bin/$t; done

ENV CC=clang CXX=clang++ \
    ASAN_SYMBOLIZER_PATH=/usr/local/bin/llvm-symbolizer
WORKDIR /travail
