#!/usr/bin/env bash
# g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c -fPIC c_priority_queue.cpp
# g++ --std=c++11 -O3 -Wall -Wextra -pedantic -shared -Wl,-soname,lib_c_priority_queue.so -o lib_c_priority_queue.so c_priority_queue.o

g++ -fdiagnostics-color=always --std=c++11 -g3 -Wall -Wextra -pedantic -c -fPIC c_priority_queue.cpp
g++ --std=c++11 -g3 -Wall -Wextra -pedantic -shared -Wl,-soname,lib_c_priority_queue.so -o lib_c_priority_queue.so c_priority_queue.o
