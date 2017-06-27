
#include <iostream>
#include <string>
#include <set>
#include <unordered_map>
#include <stdexcept>

#include "priority_queue.h"
#include "element.h"


PriorityQueue::PriorityQueue() {
  std::cerr << "NOT USING EVENTS" << std::endl;
  last_time = -1;
};

void PriorityQueue::add(const Element& element) {
  if (element_is_in(element.name)) {
    throw std::runtime_error("Element already on PriorityQueue");
  }

  if (element.get_update_time() > last_time) {
    update(element.get_update_time());
  }

  auto element_emplace_pair = elements_priority.insert(element);
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
}

Element PriorityQueue::pop(dpq_time_t current_time) {
  if (empty()) {
    throw std::out_of_range("PriorityQueue is empty");
  }
  update(current_time);
  return remove(elements_priority.begin()->name);
}

Element PriorityQueue::get_min(dpq_time_t current_time) {
  if (empty()) {
    throw std::out_of_range("PriorityQueue is empty");
  }
  update(current_time);
  return *(elements_priority.begin());
}

PriorityQueue::elements_set::const_iterator PriorityQueue::cbegin() {
  return elements_priority.cbegin();
}

PriorityQueue::elements_set::const_iterator PriorityQueue::cend() {
  return elements_priority.cend();
}

Element PriorityQueue::remove(const dpq_name_t& name) {
  auto name_map_iter = elements_name_mapper.find(name);
  return remove(name_map_iter);
}

bool PriorityQueue::empty() const {
  return elements_priority.empty();
}

bool PriorityQueue::element_is_in(const dpq_name_t& name) const {
  auto existing_element = elements_name_mapper.find(name);
  return existing_element != elements_name_mapper.end();
}

PriorityQueue::operator std::string() const {
  std::string out_str = "[ ";
  for (auto element : elements_priority) {
    out_str += std::string(element) + ", ";
  }
  if (out_str.size() == 2) {
    out_str = "[]";
  } else {
    out_str[out_str.size() - 2] = ' ';
    out_str[out_str.size() - 1] = ']';
  }

  return out_str;
}

void PriorityQueue::update(dpq_time_t current_time) {
  if (current_time == last_time) {
    return;
  }
  check_time(current_time);

  elements_name_mapper.clear();
  elements_set old_elements_priority;

  elements_priority.swap(old_elements_priority);

  for (auto element : old_elements_priority){
    element.update(current_time);
    add(element);
  }
}

void PriorityQueue::check_time(dpq_time_t current_time) {
  if (last_time > current_time) {
    throw std::runtime_error("PriorityQueue can't go back in time...");
  }
  last_time = current_time;
}

Element PriorityQueue::remove(typename elements_name_map::iterator name_map_iter) {
  if(name_map_iter == elements_name_mapper.end()) {
    throw std::runtime_error("Element not found");
  }
  auto elements_iter = name_map_iter->second;
  Element removed_element(*elements_iter);
  elements_priority.erase(elements_iter);
  elements_name_mapper.erase(name_map_iter);

  return removed_element;
}
