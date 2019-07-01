
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
  // Warning: here the higher the commitment, the worse it is
  Element(const lt_name_t& name, lt_time_t update_time, double tau,
          double system_cpu, double cpu_commitment,
          double cpu_relative_allocation, double cpu_share,
          double system_memory, double memory_commitment,
          double memory_relative_allocation, double memory_share);
  bool operator<(const Element& rhs) const;
  bool operator==(const Element& rhs) const;
  void update(lt_time_t current_time) const;
  long double get_switch_time(const Element& other_element) const;
  lt_name_t get_name() const;
  long double get_cpu_commitment() const;
  long double get_memory_commitment() const;
  long double get_priority() const;
  lt_time_t get_update_time() const;
  long double get_cpu_relative_allocation() const;
  long double get_memory_relative_allocation() const;
  void set_cpu_relative_allocation(long double cpu_relative_allocation);
  void set_memory_relative_allocation(long double memory_relative_allocation);
  operator std::string() const;

 private:
  struct Resource { // none of these values are normalized!
    Resource(long double system_total, long double commitment=0,
             long double relative_allocation=0, long double share=0);
    const long double system_total; // total amount of resources in the system
    mutable long double commitment; // non-normalized commitment
    long double relative_allocation; // non-normalized allocation
    long double share; // non-normalized share of resources that the user can
                       // use without commitment

    long double norm_allocation() const;
    long double norm_commitment() const;
    long double overused_resource() const;
    long double commitment_derivative(lt_time_t time_delta,
      long double tau) const;
    void update_commitment(lt_time_t time_delta, long double tau) const;
  };
  mutable lt_time_t update_time;
  const long double tau;
  Resource cpu;
  Resource memory;

  long double calculate_commitment(lt_time_t current_time,
    long double previous_commitment, long double relative_allocation,
    long double share) const;
  lt_time_t calculate_intersec(const Element::Resource& my_res,
    const Element::Resource& other_res, const Element& other_element) const;
  long double get_priority_derivative(lt_time_t time_delta=0.0L) const;
  const Resource& get_dominant_resource() const;
  long double get_dominant_commitment() const;
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
