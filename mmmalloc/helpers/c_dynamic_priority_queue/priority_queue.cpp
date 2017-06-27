
#include <iostream>
#include <string>
#include <set>
#include <vector>
#include <stdexcept>

#include "priority_queue.h"
#include "element.h"


PriorityQueue::PriorityQueue() {
  std::cerr << "NOT USING EVENTS" << std::endl;
  last_time = -1;
}

void PriorityQueue::add(const Element& element) {
  if (element_is_in(element.name)) {
    throw std::runtime_error("Element already on PriorityQueue");
  }

  auto element_emplace_pair = elements_priority.insert(element);
  auto element_it = element_emplace_pair.first;
  bool insertion_success = element_emplace_pair.second;
  if (!insertion_success) {
    throw std::logic_error("Element exists in elements_priority");
  }

  if (element.name >= elements_name_mapper.size()) {
    elements_name_mapper.resize(element.name+1, elements_priority.end());
  }
  elements_name_mapper[element.name] = element_it;
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
  if(name >= elements_name_mapper.size()) {
    throw std::runtime_error("Element not found: " + std::to_string(name) +
               " vector size: " + std::to_string(elements_name_mapper.size()));
  }
  auto elements_iter = elements_name_mapper.at(name);
  if(elements_iter == elements_priority.end()) {
    throw std::runtime_error("Element not found: " + std::to_string(name));
  }
  Element removed_element(*elements_iter);
  elements_priority.erase(elements_iter);
  elements_name_mapper[name] = elements_priority.end();

  return removed_element;
}

bool PriorityQueue::empty() const {
  return elements_priority.empty();
}

bool PriorityQueue::element_is_in(const dpq_name_t& name) const {
  if(name >= elements_name_mapper.size()) {
    return false;
  }
  auto existing_element = elements_name_mapper.at(name);
  return existing_element != elements_priority.end();
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
  if (last_time > current_time) {
    throw std::runtime_error("PriorityQueue can't go back in time...");
  }
  last_time = current_time;

  elements_name_mapper.reserve(elements_name_mapper.size());
  elements_name_mapper.clear();
  elements_set old_elements_priority;

  elements_priority.swap(old_elements_priority);

  for (auto element : old_elements_priority){
    element.update(current_time);
    add(element);
  }
}
