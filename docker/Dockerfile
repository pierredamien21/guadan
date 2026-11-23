# Image d'outils de guadan : tout ce qu'il faut pour compiler, tester et analyser un dépôt
# C/C++ CMake avec les sanitizers. Ubuntu 24.04 (clang 18, CMake 3.28) : voir D-12.
# Image de base figée par empreinte (liste multi-architecture), relevée le 2026-11-24
FROM ubuntu:24.04@sha256:562111b88caa79c71391c0c4d3c2114a7d5c35915c20561fd893cb1e07929e6b

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
