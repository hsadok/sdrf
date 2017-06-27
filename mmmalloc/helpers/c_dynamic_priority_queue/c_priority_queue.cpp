
#include <string>
#include <cstring>
#include <chrono>

#include "element.h"
#include "priority_queue.h"
#include "dynamic_priority_queue.h"

struct QueueTimes {
  QueueTimes() : new_t(0), add_t(0), pop_t(0), get_min_t(0), cbegin_t(0), it_next_t(0),
  get_element_from_it_t(0), it_is_end_t(0), delete_it_t(0), remove_t(0), empty_t(0),
  element_is_in_t(0), update_t(0), string_t(0), delete_t(0) {}
  std::chrono::nanoseconds new_t;
  std::chrono::nanoseconds add_t;
  std::chrono::nanoseconds pop_t;
  std::chrono::nanoseconds get_min_t;
  std::chrono::nanoseconds cbegin_t;
  std::chrono::nanoseconds it_next_t;
  std::chrono::nanoseconds get_element_from_it_t;
  std::chrono::nanoseconds it_is_end_t;
  std::chrono::nanoseconds delete_it_t;
  std::chrono::nanoseconds remove_t;
  std::chrono::nanoseconds empty_t;
  std::chrono::nanoseconds element_is_in_t;
  std::chrono::nanoseconds update_t;
  std::chrono::nanoseconds string_t;
  std::chrono::nanoseconds delete_t;
  void print_stats() {
    std::cout << "{" << std::endl;
    std::cout << "  \"new\": " << new_t.count() << "," << std::endl;
    std::cout << "  \"add\": " << add_t.count() << "," << std::endl;
    std::cout << "  \"pop\": " << pop_t.count() << "," << std::endl;
    std::cout << "  \"get_min\": " << get_min_t.count() << "," << std::endl;
    std::cout << "  \"cbegin\": " << cbegin_t.count() << "," << std::endl;
    std::cout << "  \"it_next\": " << it_next_t.count() << "," << std::endl;
    std::cout << "  \"get_element_from_it\": " << get_element_from_it_t.count() << "," << std::endl;
    std::cout << "  \"it_is_end\": " << it_is_end_t.count() << "," << std::endl;
    std::cout << "  \"delete_it\": " << delete_it_t.count() << "," << std::endl;
    std::cout << "  \"remove\": " << remove_t.count() << "," << std::endl;
    std::cout << "  \"empty\": " << empty_t.count() << "," << std::endl;
    std::cout << "  \"element_is_in\": " << element_is_in_t.count() << "," << std::endl;
    std::cout << "  \"update\": " << update_t.count() << "," << std::endl;
    std::cout << "  \"string\": " << string_t.count() << "," << std::endl;
    std::cout << "  \"delete\": " << delete_t.count() << "," << std::endl;
    std::chrono::nanoseconds total = new_t + add_t + pop_t + get_min_t
            + cbegin_t + it_next_t + get_element_from_it_t + it_is_end_t
            + delete_it_t + remove_t + empty_t + element_is_in_t + update_t
            + string_t + delete_t;
    std::cout << "  \"total\": " << total.count() << std::endl;
    std::cout << "}" << std::endl;
    
  }
};

static std::chrono::high_resolution_clock::time_point ref_time;

static QueueTimes priority_queue_times;
static QueueTimes dynamic_priority_queue_times;

extern "C" {
  typedef PriorityQueue::elements_set::const_iterator PriorityQueue_it;
  typedef DynamicPriorityQueue::elements_map::const_iterator DynamicPriorityQueue_it;

  PriorityQueue* PriorityQueue_new() {
    priority_queue_times = QueueTimes();
    ref_time = std::chrono::high_resolution_clock::now();

    PriorityQueue* ptr = new PriorityQueue();

    priority_queue_times.new_t += std::chrono::high_resolution_clock::now() - ref_time;
    return ptr;
  }
  void PriorityQueue_add(PriorityQueue* queue, Element* element) {
    ref_time = std::chrono::high_resolution_clock::now();

    queue->add(*element);

    priority_queue_times.add_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* PriorityQueue_pop(PriorityQueue* queue, double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->pop(current_time));

    priority_queue_times.pop_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  Element* PriorityQueue_get_min(PriorityQueue* queue, double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->get_min(current_time));

    priority_queue_times.get_min_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  PriorityQueue_it* PriorityQueue_cbegin(PriorityQueue* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    PriorityQueue_it* it = new PriorityQueue_it(queue->cbegin());

    priority_queue_times.cbegin_t += std::chrono::high_resolution_clock::now() - ref_time;
    return it;
  }
  void PriorityQueue_it_next(PriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    ++(*it);

    priority_queue_times.it_next_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* PriorityQueue_get_element_from_it(PriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(**it);

    priority_queue_times.get_element_from_it_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  int PriorityQueue_it_is_end(PriorityQueue* queue, PriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_end =  *it == queue->cend();

    priority_queue_times.it_is_end_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_end;
  }
  void PriorityQueue_delete_it(PriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    delete it;

    priority_queue_times.delete_it_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* PriorityQueue_remove(PriorityQueue* queue, dpq_name_t name) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->remove(name));

    priority_queue_times.remove_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  int PriorityQueue_empty(PriorityQueue* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_empty = queue->empty();

    priority_queue_times.empty_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_empty;
  }
  int PriorityQueue_element_is_in(PriorityQueue* queue, dpq_name_t name) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_in = queue->element_is_in(name);

    priority_queue_times.element_is_in_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_in;
  }
  void PriorityQueue_update(PriorityQueue* queue, double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    queue->update(current_time);

    priority_queue_times.update_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void PriorityQueue_string(PriorityQueue* queue, char* buffer, int max_size) {
    ref_time = std::chrono::high_resolution_clock::now();

    std::strncpy(buffer, std::string(*queue).c_str(), max_size);

    priority_queue_times.string_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void PriorityQueue_delete(PriorityQueue* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    delete queue;

    priority_queue_times.delete_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void PriorityQueue_print_stats() {
    priority_queue_times.print_stats();
  }


  DynamicPriorityQueue* DynamicPriorityQueue_new() {
    dynamic_priority_queue_times = QueueTimes();
    ref_time = std::chrono::high_resolution_clock::now();

    DynamicPriorityQueue* ptr = new DynamicPriorityQueue();

    dynamic_priority_queue_times.new_t += std::chrono::high_resolution_clock::now() - ref_time;
    return ptr;
  }
  void DynamicPriorityQueue_add(DynamicPriorityQueue* queue, Element* element) {
    ref_time = std::chrono::high_resolution_clock::now();

    queue->add(*element);

    dynamic_priority_queue_times.add_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* DynamicPriorityQueue_pop(DynamicPriorityQueue* queue,
                                    double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->pop(current_time));

    dynamic_priority_queue_times.pop_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  Element* DynamicPriorityQueue_get_min(DynamicPriorityQueue* queue,
                                        double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->get_min(current_time));

    dynamic_priority_queue_times.get_min_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  DynamicPriorityQueue_it* DynamicPriorityQueue_cbegin(
          DynamicPriorityQueue* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    DynamicPriorityQueue_it* it = new DynamicPriorityQueue_it(queue->cbegin());

    dynamic_priority_queue_times.cbegin_t += std::chrono::high_resolution_clock::now() - ref_time;
    return it;
  }
  void DynamicPriorityQueue_it_next(DynamicPriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    ++(*it);

    dynamic_priority_queue_times.it_next_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* DynamicPriorityQueue_get_element_from_it(
          DynamicPriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element((*it)->first);

    dynamic_priority_queue_times.get_element_from_it_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  int DynamicPriorityQueue_it_is_end(DynamicPriorityQueue* queue,
                                     DynamicPriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_end = *it == queue->cend();

    dynamic_priority_queue_times.it_is_end_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_end;
  }
  void DynamicPriorityQueue_delete_it(DynamicPriorityQueue_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    delete it;

    dynamic_priority_queue_times.delete_it_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* DynamicPriorityQueue_remove(DynamicPriorityQueue* queue,
                                       dpq_name_t name) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->remove(name));

    dynamic_priority_queue_times.remove_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  int DynamicPriorityQueue_empty(DynamicPriorityQueue* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_empty = queue->empty();

    dynamic_priority_queue_times.empty_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_empty;
  }
  int DynamicPriorityQueue_element_is_in(DynamicPriorityQueue* queue,
                                         dpq_name_t name) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_in = queue->element_is_in(name);

    dynamic_priority_queue_times.element_is_in_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_in;
  }
  void DynamicPriorityQueue_update(DynamicPriorityQueue* queue,
                                   double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    queue->update(current_time);

    dynamic_priority_queue_times.update_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void DynamicPriorityQueue_string(DynamicPriorityQueue* queue, char* buffer,
                                   int max_size) {
    ref_time = std::chrono::high_resolution_clock::now();

    std::strncpy(buffer, std::string(*queue).c_str(), max_size);

    dynamic_priority_queue_times.string_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void DynamicPriorityQueue_delete(DynamicPriorityQueue* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    delete queue;

    dynamic_priority_queue_times.delete_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void DynamicPriorityQueue_print_stats() {
    dynamic_priority_queue_times.print_stats();
  }


  Element* Element_new(dpq_name_t name, double update_time, double tau,
                       double system_cpu, double cpu_credibility,
                       double cpu_relative_allocation, double system_memory,
                       double memory_credibility,
                       double memory_relative_allocation) {
    return new Element(name, update_time, tau, system_cpu, cpu_credibility,
                       cpu_relative_allocation, system_memory,
                       memory_credibility, memory_relative_allocation);
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
  void Element_set_cpu_relative_allocation(Element* element,
                                           double cpu_relative_allocation) {
    element->set_cpu_relative_allocation(cpu_relative_allocation);
  }
  void Element_set_memory_relative_allocation(Element* element,
                                              double memory_relative_allocation)
  {
    element->set_memory_relative_allocation(memory_relative_allocation);
  }
  void Element_string(Element* element, char* buffer, int max_size) {
    std::strncpy(buffer, std::string(*element).c_str(), max_size);
  }
  void Element_delete(Element* element) {
    delete element;
  }
}
