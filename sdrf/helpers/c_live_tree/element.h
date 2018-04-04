
#ifndef ELEMENT_H
#define ELEMENT_H

#include <algorithm>
#include <functional> 
#include <string>
#include <cmath>

typedef unsigned lt_name_t;
typedef long double lt_time_t;


class Element {
 public:
  const lt_name_t name;
  // Warning: here the higher the credibility, the worse it is
  Element(const lt_name_t& name, lt_time_t update_time, double tau,
          double system_cpu, double cpu_credibility,
          double cpu_relative_allocation, double cpu_share,
          double system_memory, double memory_credibility,
          double memory_relative_allocation, double memory_share);
  bool operator<(const Element& rhs) const;
  bool operator==(const Element& rhs) const;
  void update(lt_time_t current_time) const;
  long double get_switch_time(const Element& other_element) const;
  lt_name_t get_name() const;
  long double get_cpu_credibility() const;
  long double get_memory_credibility() const;
  long double get_priority() const;
  lt_time_t get_update_time() const;
  long double get_cpu_relative_allocation() const;
  long double get_memory_relative_allocation() const;
  void set_cpu_relative_allocation(long double cpu_relative_allocation);
  void set_memory_relative_allocation(long double memory_relative_allocation);
  operator std::string() const;

 private:
  struct Resource {
    Resource(long double system_total, long double credibility=0,
             long double relative_allocation=0, long double share=0);
    const long double system_total;
    mutable long double credibility;
    long double relative_allocation;
    long double share;
  };
  mutable lt_time_t update_time;
  const long double tau;
  Resource cpu;
  Resource memory;

  long double calculate_credibility(lt_time_t current_time,
    long double previous_credibility, long double relative_allocation,
    long double share) const;
  lt_time_t get_priority_intersection(const Resource& r1,
                                       const Resource& r2) const;
  long double calculate_priority(const Resource& res, const lt_time_t time=0) const;
  long double get_priority_derivative(const Resource& r, lt_time_t time_delta) const;
  const Resource& get_dominant_resource(const lt_time_t time=0) const;
  long double get_overused_resource(const Resource& r) const;
};

namespace std {
  template<>
  struct hash<Element> {
    std::size_t operator()(const Element& e) const {
      return std::hash<lt_name_t>{}(e.name);
    }
  };
}

#endif // ELEMENT_H
