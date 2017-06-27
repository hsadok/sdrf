//
// Dynamic Priority Queue
// Priority Queue with weights that change overtime in a predictive way
//

#ifndef DYNAMIC_PRIORITY_QUEUE_H
#define DYNAMIC_PRIORITY_QUEUE_H

#include <string>
#include <set>
#include <unordered_set>
#include <map>
#include <vector>
#include <unordered_map>

#include "element.h"


/*
 * Every element in the priority queue checks if in the future they are going to
 * be switched with their right neighbor. If this is the case they calculate
 * when this is going to happen and add an event to the events set
 */
class DynamicPriorityQueue {
 public:
  typedef std::set<std::pair<dpq_time_t, dpq_name_t>> events_set; // <time, element_name>
  typedef std::map<Element, events_set::iterator> elements_map; // <element, event_it>
  typedef std::vector<elements_map::iterator> elements_name_map;

  DynamicPriorityQueue();
  void add(const Element& element);
  Element pop(dpq_time_t current_time);
  Element get_min(dpq_time_t current_time);
  elements_map::const_iterator cbegin();
  elements_map::const_iterator cend();
  Element remove(const dpq_name_t& name);
  bool empty() const;
  bool element_is_in(const dpq_name_t& name) const;
  operator std::string() const;
  void update(dpq_time_t current_time);
  void check_order();

 private:
  int events_triggered;
  int max_events;
  dpq_time_t last_time;
  events_set events;
  elements_map elements_priority; // sort elements and also link to events
  elements_name_map elements_name_mapper;

  void trigger_event(elements_map::iterator& element_it,dpq_time_t current_time,
    std::unordered_set<dpq_name_t>& pending_removal, int run=0);
  void update_event(elements_map::iterator iter);
};

#endif // DYNAMIC_PRIORITY_QUEUE_H
