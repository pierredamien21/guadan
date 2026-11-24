cmake_minimum_required(VERSION 3.16)
project(vieux_code CXX)
enable_testing()
add_executable(test_vieux test_vieux.cpp)
# Comme beaucoup de vieux projets : -Werror, qui casse avec un compilateur plus récent
target_compile_options(test_vieux PRIVATE -Wall -Werror)
add_test(NAME vieux COMMAND test_vieux)
