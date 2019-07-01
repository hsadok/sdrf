#!/usr/bin/env bash
g++ -fdiagnostics-color=always -shared -fPIC -O3 --std=c++11 -march=native -Wall -Wextra -pedantic -o lib_c_priority_queue.so c_priority_queue.cpp live_tree.cpp priority_queue.cpp element.cpp
