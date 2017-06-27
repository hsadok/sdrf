//
// Dynamic Priority Queue
// Priority Queue with weights that change overtime in a predictive way
//

#include <iostream>
#include <algorithm>
#include <functional>
#include <string>
#include <deque>
#include <set>
#include <unordered_set>
#include <map>
#include <unordered_map>
#include <stdexcept>

#include "element.h"
#include "dynamic_priority_queue.h"


DynamicPriorityQueue::DynamicPriorityQueue() {
  last_time = -1;
}

void DynamicPriorityQueue::add(const Element& element) {
  if (element_is_in(element.name)) {
    throw std::runtime_error("Element already on DynamicPriorityQueue");
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

  if (element.name >= elements_name_mapper.size()) {
    elements_name_mapper.resize(element.name+1, elements_priority.end());
  }

  elements_name_mapper[element.name] = element_it;

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

void DynamicPriorityQueue::update(dpq_time_t current_time) {
  if (last_time == current_time) {
    return;
  }
  if (last_time > current_time) {
    throw std::runtime_error("DynamicPriorityQueue can't go back in time...");
  }
  auto event_it = events.begin();

  std::unordered_set<dpq_name_t> pending_removal;
  std::deque<Element> pending_reinsertion;

  while( (event_it != events.end()) && (event_it->first < current_time) ) {
    auto element_it = elements_name_mapper.at(event_it->second);
    trigger_event(element_it, current_time, pending_removal);
    ++event_it;
  }

  for (dpq_name_t element_name : pending_removal) {
    try {
      pending_reinsertion.push_back(remove(element_name));
    }
    catch(const std::runtime_error& e) { }
  }

  last_time = current_time;

  for (const Element& element : pending_reinsertion) {
    element.update(last_time);
    add(element);
  }
//  check_order();
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

void DynamicPriorityQueue::trigger_event(elements_map::iterator& element_it,
    dpq_time_t current_time, std::unordered_set<dpq_name_t>& pending_removal) {
  pending_removal.insert(element_it->first.name);
//  if (!return_pair.second) {
//    return;
//  }
  auto neighbor_it = std::next(element_it);
  if (neighbor_it == elements_priority.end()) {
      throw std::logic_error("Event in the last element should be impossible");
  }
  pending_removal.insert(neighbor_it->first.name);

  // now check if there will be a switch for the left or for the right
  dpq_time_t switch_time;
  for (auto aux_it=std::next(neighbor_it); aux_it != elements_priority.end();
       ++aux_it) {
    switch_time = element_it->first.get_switch_time(aux_it->first);
    if ((switch_time > current_time) || (switch_time < last_time)) {
      break;
    }
    pending_removal.insert(aux_it->first.name);
  }

  elements_map::iterator aux_it_prev;
  for (auto aux_it = element_it; aux_it != elements_priority.begin();--aux_it){
    aux_it_prev = std::prev(aux_it);
    switch_time = neighbor_it->first.get_switch_time(aux_it_prev->first);
    if ((switch_time > current_time) || (switch_time < last_time)) {
      break;
    }
    pending_removal.insert(aux_it_prev->first.name);
  }
}

void DynamicPriorityQueue::update_event(elements_map::iterator iter) {
  if (iter->second != events.end()) {
    events.erase(iter->second);
  }

  if (std::next(iter) != elements_priority.end()) {
    dpq_time_t switch_time =iter->first.get_switch_time(std::next(iter)->first);
    if (switch_time >= 0) {
      auto return_pair = events.emplace(switch_time, iter->first.name);
      if (!return_pair.second) {
        throw std::logic_error("Events conflict");
      }
      iter->second = return_pair.first;
      return;
    }
  }
  iter->second = events.end();
}
