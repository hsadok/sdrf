
#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

#include <iostream>
#include <string>
#include <set>
#include <unordered_map>
#include <stdexcept>

#include "element.h"

class PriorityQueue {
 public:
  typedef std::set<Element> elements_set; // <element, event_it>
  typedef std::unordered_map<dpq_name_t, typename elements_set::iterator> elements_name_map; // <element_name, element_it>

  PriorityQueue();
  void add(const Element& element);
  Element pop(dpq_time_t current_time);
  Element get_min(dpq_time_t current_time);
  elements_set::const_iterator cbegin();
  elements_set::const_iterator cend();
  Element remove(const dpq_name_t& name);
  bool empty() const;
  bool element_is_in(const dpq_name_t& name) const;
  operator std::string() const;
  void update(dpq_time_t current_time);

 private:
  dpq_time_t last_time;
  elements_set elements_priority; // sort elements
  elements_name_map elements_name_mapper;

  void check_time(dpq_time_t current_time);
  Element remove(elements_name_map::iterator name_map_iter);
};

#endif // PRIORITY_QUEUE_H
