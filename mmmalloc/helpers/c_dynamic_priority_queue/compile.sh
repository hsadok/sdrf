#!/usr/bin/env bash
g++ -fdiagnostics-color=always -shared -fPIC -O3 --std=c++11 -Wall -Wextra -pedantic -o lib_c_priority_queue.so c_priority_queue.cpp
