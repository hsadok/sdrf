
#ifndef ELEMENT_H
#define ELEMENT_H

#include <algorithm>
#include <functional> 
#include <string>
#include <cmath>

#include "floating_point.h"

#define TIME_EPS 0.001

typedef int dpq_name_t;
typedef double dpq_time_t;


class Element {
 public:
  const dpq_name_t name;
  // Warning: here the higher the credibility, the worse it is
  Element(const dpq_name_t& name, dpq_time_t update_time, double tau,
          double system_cpu, double cpu_credibility,
          double cpu_relative_allocation, double system_memory,
          double memory_credibility, double memory_relative_allocation);
  bool operator<(const Element& rhs) const;
  bool operator==(const Element& rhs) const;
  void update(dpq_time_t current_time) const;
  double get_switch_time(const Element& other_element) const;
  dpq_name_t get_name() const;
  double get_cpu_credibility() const;
  double get_memory_credibility() const;
  double get_priority() const;
  dpq_time_t get_update_time() const;
  double get_cpu_relative_allocation() const;
  double get_memory_relative_allocation() const;
  void set_cpu_relative_allocation(double cpu_relative_allocation);
  void set_memory_relative_allocation(double memory_relative_allocation);
  operator std::string() const;

 private:
  struct Resource {
    Resource(double system_total, double credibility=0,
             double relative_allocation=0);
    const double system_total;
    mutable double credibility;
    double relative_allocation;
  };
  mutable dpq_time_t update_time;
  const double tau;
  Resource cpu;
  Resource memory;

  double calculate_credibility(dpq_time_t current_time,
    double previous_credibility, double relative_allocation) const;
  dpq_time_t get_priority_intersection(const Resource& r1, const Resource& r2)const;
  double calculate_priority(const Resource& res, const dpq_time_t time=0) const;
  double get_priority_derivative(const Resource& r, dpq_time_t time_delta)const;
  const Resource& get_dominant_resource(const dpq_time_t time=0) const;
};

namespace std {
  template<>
  struct hash<Element> {
    std::size_t operator()(const Element& e) const {
      return std::hash<dpq_name_t>{}(e.name);
    }
  };
}

#endif // ELEMENT_H
