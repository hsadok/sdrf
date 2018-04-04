
#include <ostream>
#include <iostream>
#include <fstream>
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
  void print_stats_to_stream(char* info, std::ostream& stream) {
    stream << "{" << std::endl;
    stream << "  \"info\": " << info << "," << std::endl;
    stream << "  \"new\": " << new_t.count() << "," << std::endl;
    stream << "  \"add\": " << add_t.count() << "," << std::endl;
    stream << "  \"pop\": " << pop_t.count() << "," << std::endl;
    stream << "  \"get_min\": " << get_min_t.count() << "," << std::endl;
    stream << "  \"cbegin\": " << cbegin_t.count() << "," << std::endl;
    stream << "  \"it_next\": " << it_next_t.count() << "," << std::endl;
    stream << "  \"get_element_from_it\": " << get_element_from_it_t.count() << "," << std::endl;
    stream << "  \"it_is_end\": " << it_is_end_t.count() << "," << std::endl;
    stream << "  \"delete_it\": " << delete_it_t.count() << "," << std::endl;
    stream << "  \"remove\": " << remove_t.count() << "," << std::endl;
    stream << "  \"empty\": " << empty_t.count() << "," << std::endl;
    stream << "  \"element_is_in\": " << element_is_in_t.count() << "," << std::endl;
    stream << "  \"update\": " << update_t.count() << "," << std::endl;
    stream << "  \"string\": " << string_t.count() << "," << std::endl;
    stream << "  \"delete\": " << delete_t.count() << "," << std::endl;
    std::chrono::nanoseconds total = new_t + add_t + pop_t + get_min_t
            + cbegin_t + it_next_t + get_element_from_it_t + it_is_end_t
            + delete_it_t + remove_t + empty_t + element_is_in_t + update_t
            + string_t + delete_t;
    stream << "  \"total\": " << total.count() << std::endl;
    stream << "}" << std::endl;
  }
  void print_count_to_stream(char* info, std::ostream& stream, int insert_count, int update_count, int events_count) {
    stream << "{" << std::endl;
    stream << "  \"info\": " << info << "," << std::endl;
    stream << "  \"insert_count\": " << insert_count << "," << std::endl;
    stream << "  \"update_count\": " << update_count << "," << std::endl;
    stream << "  \"events_count\": " << events_count << std::endl;
    stream << "}" << std::endl;
  }
  void print_stats(char* info, char* file_name) {
    std::ofstream out_file;
    out_file.open(file_name, std::ios_base::app);
    print_stats_to_stream(info, out_file);
    print_stats_to_stream(info, std::cout);
  }
  void print_stats(char* info, char* file_name, int insert_count, int update_count, int events_count) {
    std::ofstream out_file;
    out_file.open(file_name, std::ios_base::app);
    print_stats_to_stream(info, out_file);
    print_count_to_stream(info, out_file, insert_count, update_count, events_count);
    print_stats_to_stream(info, std::cout);
    print_count_to_stream(info, std::cout, insert_count, update_count, events_count);
  }
};

static std::chrono::high_resolution_clock::time_point ref_time;

static QueueTimes priority_queue_times;
static QueueTimes dynamic_priority_queue_times;

extern "C" {
  typedef PriorityQueue::elements_set::const_iterator PriorityQueue_it;
  typedef LiveTree::elements_map::const_iterator LiveTree_it;

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
  void PriorityQueue_print_stats(char* info, char* file_name) {
    priority_queue_times.print_stats(info, file_name);
  }


  LiveTree* LiveTree_new() {
    dynamic_priority_queue_times = QueueTimes();
    ref_time = std::chrono::high_resolution_clock::now();

    LiveTree* ptr = new LiveTree();

    dynamic_priority_queue_times.new_t += std::chrono::high_resolution_clock::now() - ref_time;
    return ptr;
  }
  void LiveTree_add(LiveTree* queue, Element* element) {
    ref_time = std::chrono::high_resolution_clock::now();

    queue->add(*element);

    dynamic_priority_queue_times.add_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* LiveTree_pop(LiveTree* queue,
                                    double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->pop(current_time));

    dynamic_priority_queue_times.pop_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  Element* LiveTree_get_min(LiveTree* queue,
                                        double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->get_min(current_time));

    dynamic_priority_queue_times.get_min_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  LiveTree_it* LiveTree_cbegin(
          LiveTree* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    LiveTree_it* it = new LiveTree_it(queue->cbegin());

    dynamic_priority_queue_times.cbegin_t += std::chrono::high_resolution_clock::now() - ref_time;
    return it;
  }
  void LiveTree_it_next(LiveTree_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    ++(*it);

    dynamic_priority_queue_times.it_next_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* LiveTree_get_element_from_it(
          LiveTree_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element((*it)->first);

    dynamic_priority_queue_times.get_element_from_it_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  int LiveTree_it_is_end(LiveTree* queue,
                                     LiveTree_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_end = *it == queue->cend();

    dynamic_priority_queue_times.it_is_end_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_end;
  }
  void LiveTree_delete_it(LiveTree_it* it) {
    ref_time = std::chrono::high_resolution_clock::now();

    delete it;

    dynamic_priority_queue_times.delete_it_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  Element* LiveTree_remove(LiveTree* queue,
                                       dpq_name_t name) {
    ref_time = std::chrono::high_resolution_clock::now();

    Element* element = new Element(queue->remove(name));

    dynamic_priority_queue_times.remove_t += std::chrono::high_resolution_clock::now() - ref_time;
    return element;
  }
  int LiveTree_empty(LiveTree* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_empty = queue->empty();

    dynamic_priority_queue_times.empty_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_empty;
  }
  int LiveTree_element_is_in(LiveTree* queue,
                                         dpq_name_t name) {
    ref_time = std::chrono::high_resolution_clock::now();

    bool is_in = queue->element_is_in(name);

    dynamic_priority_queue_times.element_is_in_t += std::chrono::high_resolution_clock::now() - ref_time;
    return is_in;
  }
  void LiveTree_update(LiveTree* queue,
                                   double current_time) {
    ref_time = std::chrono::high_resolution_clock::now();

    queue->update(current_time);

    dynamic_priority_queue_times.update_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void LiveTree_string(LiveTree* queue, char* buffer,
                                   int max_size) {
    ref_time = std::chrono::high_resolution_clock::now();

    std::strncpy(buffer, std::string(*queue).c_str(), max_size);

    dynamic_priority_queue_times.string_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void LiveTree_delete(LiveTree* queue) {
    ref_time = std::chrono::high_resolution_clock::now();

    delete queue;

    dynamic_priority_queue_times.delete_t += std::chrono::high_resolution_clock::now() - ref_time;
  }
  void LiveTree_print_stats(char* info, char* file_name) {
    int insert_count = LiveTree::get_insert_count();
    int update_count = LiveTree::get_update_count();
    int events_count = LiveTree::get_events_count();
    dynamic_priority_queue_times.print_stats(info, file_name, insert_count, update_count, events_count);
  }


  Element* Element_new(dpq_name_t name, double update_time, double tau,
                       double system_cpu, double cpu_credibility,
                       double cpu_relative_allocation, double cpu_share,
                       double system_memory, double memory_credibility,
                       double memory_relative_allocation, double memory_share){
    return new Element(name, update_time, tau, system_cpu, cpu_credibility,
                       cpu_relative_allocation, cpu_share, system_memory,
                       memory_credibility, memory_relative_allocation,
                       memory_share);
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
