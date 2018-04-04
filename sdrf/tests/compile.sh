#!/usr/bin/env bash
SOURCE_PATH=../helpers/c_live_tree
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c $SOURCE_PATH/element.cpp

g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c test_live_tree.cpp $SOURCE_PATH/live_tree.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -o test_live_tree test_live_tree.o live_tree.o element.o

g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -c test_priority_queue.cpp $SOURCE_PATH/priority_queue.cpp
g++ -fdiagnostics-color=always --std=c++11 -O3 -Wall -Wextra -pedantic -o test_priority_queue test_priority_queue.o priority_queue.o element.o
