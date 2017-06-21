
#include <string>
#include <cstring>

#include "element.h"
#include "priority_queue.h"
#include "dynamic_priority_queue.h"

typedef int name_t;

extern "C" {
  PriorityQueue<name_t>* PriorityQueue_new() {
    return new PriorityQueue<name_t>();
  }
  void PriorityQueue_add(PriorityQueue<name_t>* queue, Element<name_t>* element) {
    queue->add(*element);
  }
  Element<name_t> PriorityQueue_pop(PriorityQueue<name_t>* queue, double current_time) {
    return queue->pop(current_time);
  }
  Element<name_t> PriorityQueue_get_min(PriorityQueue<name_t>* queue, double current_time) {
    return queue->get_min(current_time);
  }
  void PriorityQueue_remove(PriorityQueue<name_t>* queue, name_t name) {
    return queue->remove(name);
  }
  int PriorityQueue_empty(PriorityQueue<name_t>* queue) {
    return queue->empty();
  }
  void PriorityQueue_update(PriorityQueue<name_t>* queue, double current_time) {
    return queue->update(current_time);
  }
  void PriorityQueue_string(PriorityQueue<name_t>* queue, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*queue).c_str(), max_size);
  }
  void PriorityQueue_delete(PriorityQueue<name_t>* queue) {
    delete queue;
  }


  DynamicPriorityQueue<name_t>* DynamicPriorityQueue_new() {
    return new DynamicPriorityQueue<name_t>();
  }
  void DynamicPriorityQueue_add(DynamicPriorityQueue<name_t>* queue, Element<name_t>* element) {
    queue->add(*element);
  }
  Element<name_t> DynamicPriorityQueue_pop(DynamicPriorityQueue<name_t>* queue, double current_time) {
    return queue->pop(current_time);
  }
  Element<name_t> DynamicPriorityQueue_get_min(DynamicPriorityQueue<name_t>* queue, double current_time) {
    std::cout << "===== 1" << std::endl;
    std::cout << "[..] last_time: " << queue->last_time << std::endl;
    return queue->get_min(current_time);
  }
  void DynamicPriorityQueue_remove(DynamicPriorityQueue<name_t>* queue, name_t name) {
    return queue->remove(name);
  }
  int DynamicPriorityQueue_empty(DynamicPriorityQueue<name_t>* queue) {
    return queue->empty();
  }
  void DynamicPriorityQueue_update(DynamicPriorityQueue<name_t>* queue, double current_time) {
    return queue->update(current_time);
  }
  void DynamicPriorityQueue_string(DynamicPriorityQueue<name_t>* queue, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*queue).c_str(), max_size);
  }
  void DynamicPriorityQueue_delete(DynamicPriorityQueue<name_t>* queue) {
    delete queue;
  }


  Element<name_t>* Element_new(name_t name, double update_time, double tau, double system_cpu,
                               double cpu_credibility, double cpu_relative_allocation,
                               double system_memory, double memory_credibility,
                               double memory_relative_allocation) {
    return new Element<name_t>(name, update_time, tau, system_cpu, cpu_credibility, cpu_relative_allocation,
                               system_memory, memory_credibility, memory_relative_allocation);
  }
  double Element_get_priority(Element<name_t>* element) {
    return element->get_priority();
  }
  double Element_get_update_time(Element<name_t>* element) {
    return element->get_update_time();
  }
  void Element_string(Element<name_t>* element, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*element).c_str(), max_size);
  }
  void Element_delete(Element<name_t>* element) {
    delete element;
  }
}
