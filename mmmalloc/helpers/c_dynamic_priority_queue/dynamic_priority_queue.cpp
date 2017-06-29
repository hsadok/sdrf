//
// Dynamic Priority Queue
// Priority Queue with weights that change overtime in a predictive way
//

#include <iostream>
#include <algorithm>
#include <functional>
#include <string>
#include <forward_list>
#include <set>
#include <map>
#include <vector>
#include <stdexcept>

#include "element.h"
#include "dynamic_priority_queue.h"

// #define LOGIC_CHECK

DynamicPriorityQueue::DynamicPriorityQueue() {
  #ifdef LOGIC_CHECK
    std::cout << "LOGIC CHECK" << std::endl;
  #endif
  last_time = -1;
}

void DynamicPriorityQueue::add(Element element) {
  dpq_name_t element_name = element.name;
  if (element_is_in(element_name)) {
    throw std::runtime_error("Element already on DynamicPriorityQueue");
  }

  if (element.get_update_time() > last_time) {
    update(element.get_update_time());
  }

  auto element_emplace_pair = elements_priority.emplace(std::move(element),
                                                        events.end());
  auto element_it = element_emplace_pair.first;
  #ifdef LOGIC_CHECK
    bool insertion_success = element_emplace_pair.second;
    if (!insertion_success) {
      throw std::logic_error("Element exists in elements_priority");
    }
  #endif

  if (element_name >= elements_name_mapper.size()) {
    elements_name_mapper.resize(element_name + 1, elements_priority.end());
  }

  elements_name_mapper[element_name] = element_it;

  if (element_it != elements_priority.begin()) {
    update_event(std::prev(element_it));
  }
  update_event(element_it);
}

Element DynamicPriorityQueue::pop(dpq_time_t current_time) {
  if (empty()) {
    throw std::out_of_range("DynamicPriorityQueue is empty");
  }
  update(current_time);
  return remove((elements_priority.begin()->first).name);
}

Element DynamicPriorityQueue::get_min(dpq_time_t current_time) {
  if (empty()) {
    throw std::out_of_range("DynamicPriorityQueue is empty");
  }
  update(current_time);
  return elements_priority.begin()->first;
}


// TODO: those iterators are leaking iterators to the internal events_set,
// not nice... They should be replaced by a custom iterator for the keys only
DynamicPriorityQueue::elements_map::const_iterator DynamicPriorityQueue::cbegin(){
  return elements_priority.cbegin();
}

DynamicPriorityQueue::elements_map::const_iterator DynamicPriorityQueue::cend(){
  return elements_priority.cend();
}

Element DynamicPriorityQueue::remove(const dpq_name_t& name) {
  if(name >= elements_name_mapper.size()) {
    throw std::runtime_error("Element not found: " + std::to_string(name) +
               " vector size: " + std::to_string(elements_name_mapper.size()));
  }
  auto elements_iter = elements_name_mapper.at(name);
  if(elements_iter == elements_priority.end()) {
    throw std::runtime_error("Element not found: " + std::to_string(name));
  }
  Element removed_element(elements_iter->first);
  auto events_iter = elements_iter->second;
  if (elements_iter != elements_priority.begin()) {
    auto prev_element = std::prev(elements_iter);
    elements_priority.erase(elements_iter);
    elements_name_mapper[name] = elements_priority.end();
    update_event(prev_element);
  } else {
    elements_priority.erase(elements_iter);
    elements_name_mapper[name] = elements_priority.end();
  }
  if (events_iter != events.end()) {
    events.erase(events_iter);
  }
  return removed_element;
}

bool DynamicPriorityQueue::empty() const {
  return elements_priority.empty();
}

bool DynamicPriorityQueue::element_is_in(const dpq_name_t& name) const {
  if(name >= elements_name_mapper.size()) {
    return false;
  }
  auto existing_element = elements_name_mapper.at(name);
  return existing_element != elements_priority.end();
}

DynamicPriorityQueue::operator std::string() const {
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

void DynamicPriorityQueue::check_order() {
  double last_priority = -100;
  for (auto element : elements_priority) {
    Element cpy(element.first);
    cpy.update(last_time);
    if (last_priority > cpy.get_priority()) {
      throw std::logic_error("DynamicPriorityQueue not properly ordered");
    }
    last_priority = cpy.get_priority();
  }
}

void DynamicPriorityQueue::update(dpq_time_t current_time) {
  if (last_time == current_time) {
    return;
  }
  if (last_time > current_time) {
    throw std::runtime_error("DynamicPriorityQueue can't go back in time...");
  }

  auto event_it = events.begin();
  if (event_it->first >= current_time) {
    return;
  }

  std::forward_list<Element> pending_reinsertion;
  elements_map::iterator element_it, neighbor_it;
  while( (event_it != events.end()) && (event_it->first < current_time) ) {
    element_it = elements_name_mapper.at(event_it->second);
    neighbor_it = std::next(element_it);
    pending_reinsertion.push_front(remove(event_it->second));
    pending_reinsertion.push_front(remove(neighbor_it->first.name));
    event_it = events.begin();
  }

  last_time = current_time;

  while(!pending_reinsertion.empty()) {
    pending_reinsertion.front().update(last_time);
    add(std::move(pending_reinsertion.front()));
    pending_reinsertion.pop_front();
  }
  #ifdef LOGIC_CHECK
    check_order();
  #endif
}

void DynamicPriorityQueue::update_event(elements_map::iterator iter) {
  if (iter->second != events.end()) {
    events.erase(iter->second);
  }

  if (std::next(iter) != elements_priority.end()) {
    dpq_time_t switch_time =iter->first.get_switch_time(std::next(iter)->first);
    if (switch_time >= 0) {
      auto return_pair = events.emplace(switch_time, iter->first.name);
      #ifdef LOGIC_CHECK
        if (!return_pair.second) {
          throw std::logic_error("Events conflict");
        }
      #endif
      iter->second = return_pair.first;
      return;
    }
  }
  iter->second = events.end();
}
