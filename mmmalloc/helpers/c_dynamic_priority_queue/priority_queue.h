
#ifndef PRIORITY_QUEUE_H
#define PRIORITY_QUEUE_H

#include <iostream>
#include <string>
#include <set>
#include <unordered_map>
#include <stdexcept>

#include "element.h"

template<typename T>
class PriorityQueue {
 public:
  typedef std::set<Element<T>> elements_set; // <element, event_it>
  typedef std::unordered_map<T, typename elements_set::iterator> elements_name_map; // <element_name, element_it>

  PriorityQueue() {
    std::cerr << "NOT USING EVENTS" << std::endl;
    last_time = -1;
  };

  void add(const Element<T>& element) {
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

  Element<T> pop(double current_time) {
    if (empty()) {
      throw std::out_of_range("PriorityQueue is empty");
    }
    update(current_time);
    return remove(elements_priority.begin()->name);
  }

  Element<T> get_min(double current_time) {
    if (empty()) {
      throw std::out_of_range("PriorityQueue is empty");
    }
    update(current_time);
    return *(elements_priority.begin());
  }

  typename elements_set::const_iterator cbegin() {
    return elements_priority.cbegin();
  }

  typename elements_set::const_iterator cend() {
    return elements_priority.cend();
  }

  Element<T> remove(const T& name) {
    auto name_map_iter = elements_name_mapper.find(name);
    return remove(name_map_iter);
  }

  bool empty() const {
    return elements_priority.empty();
  }

  bool element_is_in(const T& name) const {
    auto existing_element = elements_name_mapper.find(name);
    return existing_element != elements_name_mapper.end();
  }

  operator std::string() const {
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

  void update(double current_time) {
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

 private:
  double last_time;
  elements_set elements_priority; // sort elements
  elements_name_map elements_name_mapper;

  void check_time(double current_time) {
    if (last_time > current_time) {
      throw std::runtime_error("PriorityQueue can't go back in time...");
    }
    last_time = current_time;
  }

  Element<T> remove(typename elements_name_map::iterator name_map_iter) {
    if(name_map_iter == elements_name_mapper.end()) {
      throw std::runtime_error("Element not found");
    }
    auto elements_iter = name_map_iter->second;
    Element<T> removed_element(*elements_iter);
    elements_priority.erase(elements_iter);
    elements_name_mapper.erase(name_map_iter);

    return removed_element;
  }
};

#endif // PRIORITY_QUEUE_H
