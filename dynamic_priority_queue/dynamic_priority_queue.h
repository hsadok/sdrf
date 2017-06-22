//
// Dynamic Priority Queue
// Priority Queue with weights that change overtime in a predictive way
//

#ifndef DYNAMIC_PRIORITY_QUEUE_H
#define DYNAMIC_PRIORITY_QUEUE_H

#include <algorithm>
#include <functional>
#include <string>
#include <set>
#include <map>
#include <unordered_map>
#include <stdexcept>

#include "element.h"


/* 
 * Every element in the priority queue checks if in the future they are going to
 * be switched with their right neighbor. If this is the case they calculate
 * when this is going to happen and add an event to the events set
 */
template<typename T>
class DynamicPriorityQueue {
 public:
  typedef std::set<std::pair<double, T>> events_set; // <time, element_name>
  typedef std::map<Element<T>, typename events_set::iterator> elements_map; // <element, event_it>
  typedef std::unordered_map<T, typename elements_map::iterator> elements_name_map; // <element_name, element_it>

  DynamicPriorityQueue() {
    last_time = -1;
  };

  void add(const Element<T>& element) {
    auto existing_element = elements_name_mapper.find(element.name);
    if (existing_element !=  elements_name_mapper.end()) {
      remove(element.name);
    }

    if (element.get_update_time() > last_time) {
      update(element.get_update_time());
    }

    auto element_emplace_pair = elements_priority.emplace(element,events.end());
    auto element_it = element_emplace_pair.first;
    bool insertion_success = element_emplace_pair.second;
    if (!insertion_success) {
      throw std::logic_error("Element exists in elements_priority");
    }

    insertion_success = elements_name_mapper.emplace(element.name,
                                                     element_it).second;
    if (!insertion_success) {
      throw std::logic_error("Element exists in elements_name_mapper");
    }

    if (element_it != elements_priority.begin()) {
      update_event(std::prev(element_it));
    }
    update_event(element_it);
  }

  Element<T> pop(double current_time) {
    if (empty()) {
      throw std::out_of_range("DynamicPriorityQueue is empty");
    }
    update(current_time);
    Element<T> first_element(elements_priority.begin()->first);
    remove(first_element.name);
    return first_element;
  }

  Element<T> get_min(double current_time) {
    if (empty()) {
      throw std::out_of_range("DynamicPriorityQueue is empty");
    }
    update(current_time);
    return elements_priority.begin()->first;
  }


  // TODO: those iterators are leaking iterators to the internal events_set,
  // not nice... They should be replaced by a custom iterator for the keys only
  typename elements_map::const_iterator cbegin() {
    return elements_priority.cbegin();
  }

  typename elements_map::const_iterator cend() {
    return elements_priority.cend();
  }

  void remove(const T& name) {
    auto name_map_iter = elements_name_mapper.find(name);
    remove(name_map_iter);
  }

  bool empty() const {
    return elements_priority.empty();
  }

  operator std::string() const {
    std::string out_str = "[ ";
    for (auto element : elements_priority) {
      out_str += std::string(element.first) + ", ";
    }
    if (out_str.size() == 2) {
      out_str = "[]";
    } else {
      out_str[out_str.size() - 2] = ' ';
      out_str[out_str.size() - 1] = ']';
    }

    return out_str;
  }

  void update(double current_time) {
    check_time(current_time);
    auto event_it = events.begin();
    while( !events.empty() && (event_it->first <= current_time) ) {
      trigger_event(event_it->second, current_time);
      event_it = events.begin();
    }
  }

 private:
  double last_time;
  events_set events; 
  elements_map elements_priority; // sort elements and also link to events
  elements_name_map elements_name_mapper;

  void trigger_event(T name, double current_time) {
    // == Example when there are ties ==
    // [A] > [B] = [C] = [D] > [E] > [F]
    //
    // Making E > D (element=D, neighbor=E):
    // [A] > [B] = [C] = [D]   [E] > [F]
    // iterators:         ^     ^     ^
    //
    // Removing D and E:
    // [A] > [B] = [C] > [F]
    // iterators:         ^
    //
    // Insert E:
    // [A] > [E] > [B] = [C] > [F]
    //        ^                 ^
    //
    // Insert D:
    // [A] > [E] > [B] = [C] = [D] > [F]
    //        ^                 ^     ^
    //
    // Now update events for D, C, E and A

    auto element_it = elements_name_mapper.at(name);
    auto neighbor_it = std::next(element_it);

    if (neighbor_it == elements_priority.end()) {
      throw std::logic_error("Event in the last element should be impossible");
    }

    const auto reference_it = std::next(neighbor_it);

    auto element = *element_it;
    auto neighbor = *neighbor_it;

    elements_priority.erase(element_it);
    elements_priority.erase(neighbor_it);

    element.first.update(current_time);
    neighbor.first.update(current_time);

    // we are supercareful to insert elements back in O(1), since we know
    // exactly where they are going, but hints may not help if there are ties
    neighbor_it = elements_priority.insert(reference_it, neighbor);
    element_it = elements_priority.insert(reference_it, element);
    
    elements_name_mapper[name] = element_it;
    elements_name_mapper[neighbor_it->first.name] = neighbor_it;

    update_event(element_it);
    update_event(neighbor_it);
    if (neighbor_it != std::prev(element_it)) { // there are ties
      update_event(std::prev(element_it));
    }
    if (neighbor_it != elements_priority.begin()){
      update_event(std::prev(neighbor_it));
    }
  }

  void update_event(typename elements_map::iterator iter) {
    if (iter->second != events.end()) {
      events.erase(iter->second);
    }

    if (std::next(iter) != elements_priority.end()) {
      double switch_time = iter->first.get_switch_time(std::next(iter)->first);
      if (switch_time >= 0) {
        auto event_iter = events.emplace(switch_time, iter->first.name).first;
        iter->second = event_iter;
        return;
      }
    }
    iter->second = events.end();
  }

  void check_time(double current_time) {
    if (last_time > current_time) {
      throw std::runtime_error("DynamicPriorityQueue can't go back in time...");
    }
    last_time = current_time;
  }

  void remove(typename elements_name_map::iterator name_map_iter) {
    if(name_map_iter == elements_name_mapper.end()) {
      return;
    }
    auto elements_iter = name_map_iter->second;
    auto events_iter = elements_iter->second;
    if (elements_iter != elements_priority.begin()) {
      auto prev_element = std::prev(elements_iter);
      elements_priority.erase(elements_iter);
      elements_name_mapper.erase(name_map_iter);
      update_event(prev_element);
    } else {
      elements_priority.erase(elements_iter);
      elements_name_mapper.erase(name_map_iter);
    }

    if (events_iter != events.end()) {
      events.erase(events_iter);
    }
  }
};

#endif // DYNAMIC_PRIORITY_QUEUE_H
