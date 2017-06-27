
#include <string>
#include <cstring>

#include "element.h"
#include "priority_queue.h"
#include "dynamic_priority_queue.h"

extern "C" {
  typedef PriorityQueue::elements_set::const_iterator PriorityQueue_it;
  typedef DynamicPriorityQueue::elements_map::const_iterator DynamicPriorityQueue_it;

  PriorityQueue* PriorityQueue_new() {
    return new PriorityQueue();
  }
  void PriorityQueue_add(PriorityQueue* queue, Element* element) {
    queue->add(*element);
  }
  Element* PriorityQueue_pop(PriorityQueue* queue, double current_time) {
    Element* element = new Element(queue->pop(current_time));
    return element;
  }
  Element* PriorityQueue_get_min(PriorityQueue* queue, double current_time) {
    Element* element = new Element(queue->get_min(current_time));
    return element;
  }
  PriorityQueue_it* PriorityQueue_cbegin(PriorityQueue* queue) {
    PriorityQueue_it* it = new PriorityQueue_it(queue->cbegin());
    return it;
  }
  void PriorityQueue_it_next(PriorityQueue_it* it) {
    ++(*it);
  }
  Element* PriorityQueue_get_element_from_it(PriorityQueue_it* it) {
    Element* element = new Element(**it);
    return element;
  }
  int PriorityQueue_it_is_end(PriorityQueue* queue, PriorityQueue_it* it) {
    return *it == queue->cend();
  }
  void PriorityQueue_delete_it(PriorityQueue_it* it) {
    delete it;
  }
  Element* PriorityQueue_remove(PriorityQueue* queue, dpq_name_t name) {
    Element* element = new Element(queue->remove(name));
    return element;
  }
  int PriorityQueue_empty(PriorityQueue* queue) {
    return queue->empty();
  }
  int PriorityQueue_element_is_in(PriorityQueue* queue, dpq_name_t name) {
    return queue->element_is_in(name);
  }
  void PriorityQueue_update(PriorityQueue* queue, double current_time) {
    return queue->update(current_time);
  }
  void PriorityQueue_string(PriorityQueue* queue, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*queue).c_str(), max_size);
  }
  void PriorityQueue_delete(PriorityQueue* queue) {
    delete queue;
  }


  DynamicPriorityQueue* DynamicPriorityQueue_new() {
    return new DynamicPriorityQueue();
  }
  void DynamicPriorityQueue_add(DynamicPriorityQueue* queue, Element* element) {
    queue->add(*element);
  }
  Element* DynamicPriorityQueue_pop(DynamicPriorityQueue* queue, double current_time) {
    Element* element = new Element(queue->pop(current_time));
    return element;
  }
  Element* DynamicPriorityQueue_get_min(DynamicPriorityQueue* queue, double current_time) {
    Element* element = new Element(queue->get_min(current_time));
    return element;
  }
  DynamicPriorityQueue_it* DynamicPriorityQueue_cbegin(DynamicPriorityQueue* queue) {
    DynamicPriorityQueue_it* it = new DynamicPriorityQueue_it(queue->cbegin());
    return it;
  }
  void DynamicPriorityQueue_it_next(DynamicPriorityQueue_it* it) {
    ++(*it);
  }
  Element* DynamicPriorityQueue_get_element_from_it(DynamicPriorityQueue_it* it) {
    Element* element = new Element((*it)->first);
    return element;
  }
  int DynamicPriorityQueue_it_is_end(DynamicPriorityQueue* queue, DynamicPriorityQueue_it* it) {
    return *it == queue->cend();
  }
  void DynamicPriorityQueue_delete_it(DynamicPriorityQueue_it* it) {
    delete it;
  }
  Element* DynamicPriorityQueue_remove(DynamicPriorityQueue* queue, dpq_name_t name) {
    Element* element = new Element(queue->remove(name));
    return element;
  }
  int DynamicPriorityQueue_empty(DynamicPriorityQueue* queue) {
    return queue->empty();
  }
  int DynamicPriorityQueue_element_is_in(DynamicPriorityQueue* queue, dpq_name_t name) {
    return queue->element_is_in(name);
  }
  void DynamicPriorityQueue_update(DynamicPriorityQueue* queue, double current_time) {
    return queue->update(current_time);
  }
  void DynamicPriorityQueue_string(DynamicPriorityQueue* queue, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*queue).c_str(), max_size);
  }
  void DynamicPriorityQueue_delete(DynamicPriorityQueue* queue) {
    delete queue;
  }


  Element* Element_new(dpq_name_t name, double update_time, double tau, double system_cpu,
                               double cpu_credibility, double cpu_relative_allocation,
                               double system_memory, double memory_credibility,
                               double memory_relative_allocation) {
    return new Element(name, update_time, tau, system_cpu, cpu_credibility, cpu_relative_allocation,
                               system_memory, memory_credibility, memory_relative_allocation);
  }
  void Element_update(Element* element, double current_time) {
    element->update(current_time);
  }
  dpq_name_t Element_get_name(Element* element) {
    return element->get_name();
  }
  double Element_get_cpu_credibility(Element* element) {
    return element->get_cpu_credibility();
  }
  double Element_get_memory_credibility(Element* element) {
    return element->get_memory_credibility();
  }
  double Element_get_priority(Element* element) {
    return element->get_priority();
  }
  double Element_get_update_time(Element* element) {
    return element->get_update_time();
  }
  double Element_get_cpu_relative_allocation(Element* element) {
    return element->get_cpu_relative_allocation();
  }
  double Element_get_memory_relative_allocation(Element* element) {
    return element->get_memory_relative_allocation();
  }
  void Element_set_cpu_relative_allocation(Element* element, double cpu_relative_allocation) {
    element->set_cpu_relative_allocation(cpu_relative_allocation);
  }
  void Element_set_memory_relative_allocation(Element* element, double memory_relative_allocation) {
    element->set_memory_relative_allocation(memory_relative_allocation);
  }
  void Element_string(Element* element, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*element).c_str(), max_size);
  }
  void Element_delete(Element* element) {
    delete element;
  }
}
