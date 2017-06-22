
#include <string>
#include <cstring>

#include "element.h"
#include "priority_queue.h"
#include "dynamic_priority_queue.h"

extern "C" {
  typedef int name_t;
  typedef PriorityQueue<name_t>::elements_set::const_iterator PriorityQueue_it;
  typedef DynamicPriorityQueue<name_t>::elements_map::const_iterator DynamicPriorityQueue_it;

  PriorityQueue<name_t>* PriorityQueue_new() {
    return new PriorityQueue<name_t>();
  }
  void PriorityQueue_add(PriorityQueue<name_t>* queue, Element<name_t>* element) {
    queue->add(*element);
  }
  Element<name_t>* PriorityQueue_pop(PriorityQueue<name_t>* queue, double current_time) {
    Element<name_t>* element = new Element<name_t>(queue->pop(current_time));
    return element;
  }
  Element<name_t>* PriorityQueue_get_min(PriorityQueue<name_t>* queue, double current_time) {
    Element<name_t>* element = new Element<name_t>(queue->get_min(current_time));
    return element;
  }
  PriorityQueue_it* PriorityQueue_cbegin(PriorityQueue<name_t>* queue) {
    PriorityQueue_it* it = new PriorityQueue_it(queue->cbegin());
    return it;
  }
  void PriorityQueue_it_next(PriorityQueue_it* it) {
    ++(*it);
  }
  Element<name_t>* PriorityQueue_get_element_from_it(PriorityQueue_it* it) {
    Element<name_t>* element = new Element<name_t>(**it);
    return element;
  }
  int PriorityQueue_it_is_end(PriorityQueue<name_t>* queue, PriorityQueue_it* it) {
    return *it == queue->cend();
  }
  void PriorityQueue_delete_it(PriorityQueue_it* it) {
    delete it;
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
  Element<name_t>* DynamicPriorityQueue_pop(DynamicPriorityQueue<name_t>* queue, double current_time) {
    Element<name_t>* element = new Element<name_t>(queue->pop(current_time));
    return element;
  }
  Element<name_t>* DynamicPriorityQueue_get_min(DynamicPriorityQueue<name_t>* queue, double current_time) {
    Element<name_t>* element = new Element<name_t>(queue->get_min(current_time));
    return element;
  }
  DynamicPriorityQueue_it* DynamicPriorityQueue_cbegin(DynamicPriorityQueue<name_t>* queue) {
    DynamicPriorityQueue_it* it = new DynamicPriorityQueue_it(queue->cbegin());
    return it;
  }
  void DynamicPriorityQueue_it_next(DynamicPriorityQueue_it* it) {
    ++(*it);
  }
  Element<name_t>* DynamicPriorityQueue_get_element_from_it(DynamicPriorityQueue_it* it) {
    Element<name_t>* element = new Element<name_t>((*it)->first);
    return element;
  }
  int DynamicPriorityQueue_it_is_end(DynamicPriorityQueue<name_t>* queue, DynamicPriorityQueue_it* it) {
    return *it == queue->cend();
  }
  void DynamicPriorityQueue_delete_it(DynamicPriorityQueue_it* it) {
    delete it;
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
