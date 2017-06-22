#!/usr/bin/env bash
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c test_dynamic_priority_queue.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -o test_dynamic_priority_queue test_dynamic_priority_queue.o

g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c test_priority_queue.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -o test_priority_queue test_priority_queue.o

g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c -fPIC c_priority_queue.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -shared -Wl,-soname,lib_c_priority_queue.so -o lib_c_priority_queue.so c_priority_queue.o
