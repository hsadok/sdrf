// compile with:
// g++ --std=c++11 -Wall -Wextra -pedantic -c test_dynamic_priority_queue.cpp
// g++ --std=c++11 -Wall -Wextra -pedantic -o test_dynamic_priority_queue test_dynamic_priority_queue.o

#include <iostream>
#include <string>
#include <cassert>
#include <cmath>

#include "dynamic_priority_queue.h"


int main()
{
  double system_cpu = 20.0;
  double system_memory = 100.0;
  double delta = 0.9999;
  double tau = -1/log(delta);

  double update_time = 1.0;

  DynamicPriorityQueue<int> queue = DynamicPriorityQueue<int>();

  double c_o_cpu = -8.0;
  double c_o_mem = 1.0;
  double o_cpu = 5.0;
  double o_mem = 5.0;
  Element<int> e1 = Element<int>(10, update_time, tau, system_cpu, c_o_cpu, o_cpu,
    system_memory, c_o_mem, o_mem);
  queue.add(e1);

  queue.get_min(1);

  // std::cout << std::string(queue) << std::endl;

  // c_o_cpu = -8.0;
  // c_o_mem = 3.3;
  // o_cpu = 0.0;
  // o_mem = 3.3;
  // Element<int> e2 = Element<int>(5, update_time, tau, system_cpu, c_o_cpu, o_cpu,
  //   system_memory, c_o_mem, o_mem);
  // queue.add(e2);
  // std::cout << std::string(queue) << std::endl;

  // update_time = 7816;
  // queue.update(update_time);
  // std::cout << std::string(queue) << std::endl;

  // std::cout << "min: " << std::string(queue.get_min(update_time)) << std::endl;
  // std::cout << "min: " << std::string(queue.pop(update_time)) << std::endl;
  // std::cout << "min: " << std::string(queue.pop(update_time)) << std::endl;
  // std::cout << std::string(queue) << std::endl;

  // c_o_cpu = -8.0;
  // c_o_mem = 1.0;
  // o_cpu = 5.0;
  // o_mem = 5.0;
  // Element<int> e3 = Element<int>(10, update_time, tau, system_cpu, c_o_cpu, o_cpu,
  //   system_memory, c_o_mem, o_mem);
  // queue.add(e3);
  // queue.add(e2);
  // std::cout << std::string(queue) << std::endl;

  // update_time += 2000;
  // queue.update(update_time);
  // std::cout << std::string(queue) << std::endl;

  // update_time += 2000;
  // queue.update(update_time);
  // std::cout << std::string(queue) << std::endl;

  // update_time += 2000;
  // queue.update(update_time);
  // std::cout << std::string(queue) << std::endl;

  // update_time += 2000;
  // queue.update(update_time);
  // std::cout << std::string(queue) << std::endl;

  // std::cout << "remove" <<std::endl;

  // queue.remove(10);
  // queue.remove(10);
  // std::cout << std::string(queue) << std::endl;

  // queue.add(e3);
  // std::cout << std::string(queue) << std::endl;

  // queue.remove(7);
  // std::cout << std::string(queue) << std::endl;

  // TODO check if element modified externally modifies container

  return 0;
}
