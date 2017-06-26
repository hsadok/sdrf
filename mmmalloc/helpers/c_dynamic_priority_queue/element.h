
#ifndef ELEMENT_H
#define ELEMENT_H

#include <algorithm>
#include <functional>
#include <string>
#include <stdexcept>

#include <cmath>

#include "floating_point.h"

#define TIME_EPS 0.001

template<typename T>
class Element {
 public:
  const T name;
  // Warning: here the higher the credibility, the worse it is
  Element(const T& name, double update_time, double tau, double system_cpu,
          double cpu_credibility, double cpu_relative_allocation,
          double system_memory, double memory_credibility,
          double memory_relative_allocation)
          : name(name), update_time(update_time), tau(tau),
            cpu(system_cpu, cpu_credibility, cpu_relative_allocation),
            memory(system_memory, memory_credibility,memory_relative_allocation)
  { }

  ~Element() { }

  bool operator<(const Element& rhs) const {
    // it's not really necessary to update the other element, however it's
    // easier to implement. However this assumes the queue is already updated to
    // the most recent update_time
    if (update_time > rhs.update_time) {
      rhs.update(update_time);
    } else {
      update(rhs.update_time);
    }
    double my_priority = get_priority();
    double rhs_priority = rhs.get_priority();

    const FloatingPoint<float> fp_my_priority(my_priority);
    const FloatingPoint<float> fp_rhs_priority(rhs_priority);
    if (!fp_my_priority.AlmostEquals(fp_rhs_priority)) {
      return my_priority < rhs_priority;
    }

    const Resource& my_dominant_resource = get_dominant_resource(update_time);
    const Resource& rhs_dominant_resource = rhs.get_dominant_resource(update_time);
    double my_growth = get_priority_derivative(my_dominant_resource, 0);
    double rhs_growth = get_priority_derivative(rhs_dominant_resource, 0);

    const FloatingPoint<float> fp_my_growth(my_growth);
    const FloatingPoint<float> fp_rhs_growth(rhs_growth);
    if (!fp_my_growth.AlmostEquals(fp_rhs_growth)) {
      return my_growth < rhs_growth;
    }

    // Too close, we now get the switch time and if positive we consider the
    // order as is, otherwise we invert it
    double switch_time = get_switch_time(rhs);
    if (switch_time < 0) {
      return my_priority < rhs_priority;
    }
    if (switch_time > 0) {
      if ((switch_time - update_time) < TIME_EPS) {
        return my_priority > rhs_priority;
      }
      return my_priority < rhs_priority;
    }
    return name < rhs.name;
  }

  bool operator==(const Element& rhs) const {
    return this->name == rhs.name;
  }

  void update(double current_time) const {
    if (current_time == update_time) {
      return;
    }
    if (current_time < update_time) {
      throw std::runtime_error("Can't update Element to the past");
    }
    cpu.credibility = calculate_credibility(current_time, cpu.credibility,
                                            cpu.relative_allocation);
    memory.credibility = calculate_credibility(current_time, memory.credibility,
                                               memory.relative_allocation);

    update_time = current_time;
  }

  double get_switch_time(const Element& other_element) const {
    if (other_element.update_time > update_time) {
      update(other_element.update_time);
    } else {
      other_element.update(update_time);
    }

    // first define self-intersections, these breaks will define the regimes;
    // for 2 resources there is a maximum of 3 regimes
    double self_intersec = get_priority_intersection(cpu, memory);
    double other_intersec = get_priority_intersection(other_element.cpu,
                                                      other_element.memory);

    if (!std::isfinite(self_intersec)) {
      self_intersec = -1;
    }

    if (!std::isfinite(other_intersec)) {
      other_intersec = -2;
    }

    double min_intersec = std::min(self_intersec, other_intersec);
    double max_intersec = std::max(self_intersec, other_intersec);

    if (min_intersec <= 0) {
      min_intersec = max_intersec;
    }

    double t;
    double intersection;
    // regime 1: t in (0, min_intersec)
    if (min_intersec > 0) {
      t = update_time + min_intersec/2;
      const Resource& self_domin_res = get_dominant_resource(t);
      const Resource& other_domin_res =other_element.get_dominant_resource(t);
      intersection = get_priority_intersection(self_domin_res, other_domin_res);
      if (std::isfinite(intersection) &&
          (intersection > 0) && (intersection < min_intersec)) {
        return update_time + intersection;
      }

      // regime 2: t in [min_intersec, max_intersec)
      if (min_intersec < max_intersec) {
        t = update_time + (min_intersec + max_intersec)/2;
        const Resource& self_domin_res = get_dominant_resource(t);
        const Resource& other_domin_res = other_element.get_dominant_resource(t);
        intersection=get_priority_intersection(self_domin_res, other_domin_res);
        if (std::isfinite(intersection) && (intersection > 0) &&
           (intersection >= min_intersec) && (intersection < max_intersec)) {
          t = update_time + intersection;
          if (intersection == min_intersec) {
            // we can't know for sure if the intersection causes a switch
            // so we compare the derivatives
            if (get_priority_derivative(self_domin_res, intersection) >
                get_priority_derivative(other_domin_res, intersection)) {
              return t;
            }
          }
          return t;
        }
      }
    }

    // regime 3: t in [max(min_intersec, max_intersec, 0), +inf)
    t = update_time + std::max(max_intersec, 0.0) + 1;
    const Resource& self_domin_res = get_dominant_resource(t);
    const Resource& other_domin_res = other_element.get_dominant_resource(t);
    intersection=get_priority_intersection(self_domin_res, other_domin_res);
    if (std::isfinite(intersection) && (intersection > 0) &&
       (intersection >= max_intersec)) {
      t = update_time + intersection;
      if (intersection == max_intersec) {
        // we can't know for sure if the intersection causes a switch
        // so we compare the derivatives
        if (get_priority_derivative(self_domin_res, intersection) >
            get_priority_derivative(other_domin_res, intersection)) {
          return t;
        }
      }
      return update_time + intersection;
    }
    return -1;
  }

  T get_name() const {
    return name;
  }

  double get_cpu_credibility() const {
    return cpu.credibility;
  }

  double get_memory_credibility() const {
    return memory.credibility;
  }

  double get_priority() const {
    return std::max(calculate_priority(cpu), calculate_priority(memory));
  }

  double get_update_time() const {
    return update_time;
  }

  double get_cpu_relative_allocation() const {
    return cpu.relative_allocation;
  }

  double get_memory_relative_allocation() const {
    return memory.relative_allocation;
  }

  void set_cpu_relative_allocation(double cpu_relative_allocation) {
    cpu.relative_allocation = cpu_relative_allocation;
  }

  void set_memory_relative_allocation(double memory_relative_allocation) {
    memory.relative_allocation = memory_relative_allocation;
  }

  operator std::string() const {
    return std::to_string(name) + "(" + std::to_string(get_priority()) + ")";
  }

 private:
  struct Resource {
    Resource(double system_total, double credibility=0,
             double relative_allocation=0)
            : system_total(system_total), credibility(credibility),
              relative_allocation(relative_allocation) { }
    const double system_total;
    mutable double credibility;
    double relative_allocation;
  };
  mutable double update_time;
  const double tau;
  Resource cpu;
  Resource memory;

  double calculate_credibility(double current_time, double previous_credibility,
                               double relative_allocation) const
  {
    double delta_t = current_time - update_time;
    double alpha = 1 - std::exp(-delta_t/tau);
    return previous_credibility + alpha * (relative_allocation
                                           - previous_credibility);
  }

  double get_priority_intersection(const Resource& r1, const Resource& r2)const{
    return tau * std::log(
            0.5 * (1 + (r1.system_total * r2.credibility
                        - r2.system_total * r1.credibility) /
                       (r2.system_total * r1.relative_allocation
                        - r1.system_total * r2.relative_allocation)
                  )
    );
  }

  double calculate_priority(const Resource& res, const double time=0) const {
    double credibility = res.credibility;
    if (time != 0) {
      credibility = calculate_credibility(time, credibility,
                                          res.relative_allocation);
    }
    return (res.relative_allocation + credibility) / res.system_total;
  }

  double get_priority_derivative(const Resource& r, double time_delta) const {
    return (r.relative_allocation + r.credibility)/(r.system_total * tau)
           * std::exp(-time_delta/tau);
  }

  const Resource& get_dominant_resource(const double time=0) const {
    if (calculate_priority(cpu, time) < calculate_priority(memory, time)) {
      return memory;
    }
    return cpu;
  }
};

namespace std {
  template<typename T>
  struct hash<Element<T>>
  {
    std::size_t operator()(const Element<T>& e) const
    {
      return std::hash<T>{}(e.name);
    }
  };
}

#endif // ELEMENT_H
