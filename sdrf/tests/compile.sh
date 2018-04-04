#!/usr/bin/env bash
SOURCE_PATH=../helpers/c_dynamic_priority_queue
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c $SOURCE_PATH/element.cpp

g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c test_dynamic_priority_queue.cpp $SOURCE_PATH/dynamic_priority_queue.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -o test_dynamic_priority_queue test_dynamic_priority_queue.o dynamic_priority_queue.o element.o

g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c test_priority_queue.cpp $SOURCE_PATH/priority_queue.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -o test_priority_queue test_priority_queue.o priority_queue.o element.o
