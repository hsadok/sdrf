
#include <iostream>
#include <algorithm>
#include <functional>
#include <string>
#include <stdexcept>

#include <cmath>

#include "element.h"


Element::Element(const dpq_name_t& name, dpq_time_t update_time, double tau,
  double system_cpu, double cpu_credibility, double cpu_relative_allocation,
  double system_memory, double memory_credibility,
  double memory_relative_allocation)
  : name(name), update_time(update_time), tau(tau),
    cpu(system_cpu, cpu_credibility, cpu_relative_allocation),
    memory(system_memory, memory_credibility,memory_relative_allocation)
  { }

bool Element::operator<(const Element& rhs) const {
  // it's not really necessary to update the other element, however it's
  // easier to implement. This assumes the queue is already updated to the most
  // recent update_time
  if (update_time > rhs.update_time) {
    rhs.update(update_time);
  } else {
    update(rhs.update_time);
  }
  double my_priority = get_priority();
  double rhs_priority = rhs.get_priority();
  if (my_priority != rhs_priority) {
    return my_priority < rhs_priority;
  }

  const Element::Resource& my_dominant_resource =
          get_dominant_resource(update_time);
  const Element::Resource& rhs_dominant_resource =
          rhs.get_dominant_resource(update_time);
  double my_growth = get_priority_derivative(my_dominant_resource, 0);
  double rhs_growth = get_priority_derivative(rhs_dominant_resource, 0);
  if (std::isfinite(my_growth) && std::isfinite(rhs_growth) &&
      my_growth != rhs_growth)
  {
    return my_growth < rhs_growth;
  }

  return name < rhs.name;
}

bool Element::operator==(const Element& rhs) const {
  return this->name == rhs.name;
}

void Element::update(dpq_time_t current_time) const {
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

dpq_time_t Element::get_switch_time(const Element& other_element) const {
  if (other_element.update_time > update_time) {
    update(other_element.update_time);
  } else {
    other_element.update(update_time);
  }

  // first define self-intersections, these breaks will define the regimes;
  // for 2 resources there is a maximum of 3 regimes
  dpq_time_t self_intersec = get_priority_intersection(cpu, memory);
  dpq_time_t other_intersec = get_priority_intersection(other_element.cpu,
                                                    other_element.memory);

  if (!std::isfinite(self_intersec)) {
    self_intersec = -1;
  }

  if (!std::isfinite(other_intersec)) {
    other_intersec = -2;
  }

  dpq_time_t min_intersec = std::min(self_intersec, other_intersec);
  dpq_time_t max_intersec = std::max(self_intersec, other_intersec);

  if (min_intersec <= 0) {
    min_intersec = max_intersec;
  }

  dpq_time_t t;
  dpq_time_t intersection;
  // regime 1: t in (0, min_intersec)
  if (min_intersec > 0) {
    t = update_time + min_intersec/2;
    const Element::Resource& self_domin_res = get_dominant_resource(t);
    const Element::Resource& other_domin_res =
            other_element.get_dominant_resource(t);
    intersection = get_priority_intersection(self_domin_res, other_domin_res);
    if (std::isfinite(intersection) &&
        (intersection > 0) && (intersection < min_intersec)) {
      return update_time + intersection;
    }

    // regime 2: t in [min_intersec, max_intersec)
    if (min_intersec < max_intersec) {
      t = update_time + (min_intersec + max_intersec)/2;
      const Element::Resource& self_domin_res = get_dominant_resource(t);
      const Element::Resource& other_domin_res =
              other_element.get_dominant_resource(t);
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
  const Element::Resource& self_domin_res = get_dominant_resource(t);
  const Element::Resource& other_domin_res =
          other_element.get_dominant_resource(t);
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

dpq_name_t Element::get_name() const {
  return name;
}

double Element::get_cpu_credibility() const {
  return cpu.credibility;
}

double Element::get_memory_credibility() const {
  return memory.credibility;
}

double Element::get_priority() const {
  return std::max(calculate_priority(cpu), calculate_priority(memory));
}

dpq_time_t Element::get_update_time() const {
  return update_time;
}

double Element::get_cpu_relative_allocation() const {
  return cpu.relative_allocation;
}

double Element::get_memory_relative_allocation() const {
  return memory.relative_allocation;
}

void Element::set_cpu_relative_allocation(double cpu_relative_allocation) {
  cpu.relative_allocation = cpu_relative_allocation;
}

void Element::set_memory_relative_allocation(double memory_relative_allocation){
  memory.relative_allocation = memory_relative_allocation;
}

Element::operator std::string() const {
  return std::to_string(name) + "(" + std::to_string(get_priority()) + ")";
}

Element::Resource::Resource(double system_total, double credibility,
   double relative_allocation)
   : system_total(system_total), credibility(credibility),
     relative_allocation(relative_allocation) { }

double Element::calculate_credibility(dpq_time_t current_time,
    double previous_credibility, double relative_allocation) const {
  dpq_time_t delta_t = current_time - update_time;
  double alpha = 1 - std::exp(-delta_t/tau);
  return previous_credibility + alpha * (relative_allocation
                                         - previous_credibility);
}

dpq_time_t Element::get_priority_intersection(const Element::Resource& r1,
                                              const Element::Resource& r2)const{
  return tau * std::log(
          0.5 * (1 + (r1.system_total * r2.credibility
                      - r2.system_total * r1.credibility) /
                     (r2.system_total * r1.relative_allocation
                      - r1.system_total * r2.relative_allocation)
                )
  );
}

double Element::calculate_priority(const Element::Resource& res,
                                   const dpq_time_t time) const {
  double credibility = res.credibility;
  if (time != 0) {
    credibility = calculate_credibility(time, credibility,
                                        res.relative_allocation);
  }
  return (res.relative_allocation + credibility) / res.system_total;
}

double Element::get_priority_derivative(const Element::Resource& r,
    dpq_time_t time_delta) const {
  return (r.relative_allocation - r.credibility)/(r.system_total * tau)
         * std::exp(-time_delta/tau);
}

const Element::Resource& Element::get_dominant_resource(
        const dpq_time_t time) const {
  if (calculate_priority(cpu, time) < calculate_priority(memory, time)) {
    return memory;
  }
  return cpu;
}
