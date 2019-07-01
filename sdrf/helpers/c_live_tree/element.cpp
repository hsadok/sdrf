
#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

#include "element.h"


Element::Element(const lt_name_t& name, lt_time_t update_time, double tau,
  double system_cpu, double cpu_commitment, double cpu_relative_allocation,
  double cpu_share, double system_memory, double memory_commitment,
  double memory_relative_allocation, double memory_share)
  : name(name), update_time(update_time), tau(tau),
    cpu(system_cpu, cpu_commitment, cpu_relative_allocation, cpu_share),
    memory(system_memory, memory_commitment, memory_relative_allocation,
           memory_share)
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
  long double my_priority = get_priority();
  long double rhs_priority = rhs.get_priority();
  if (my_priority != rhs_priority) {
    return my_priority < rhs_priority;
  }

  my_priority = get_priority_derivative();
  rhs_priority = rhs.get_priority_derivative();
  if (my_priority != rhs_priority) {
    return my_priority < rhs_priority;
  }

  return name < rhs.name; // they grow together, use name for consistency
}

bool Element::operator==(const Element& rhs) const {
  return this->name == rhs.name;
}

void Element::update(lt_time_t next_update_time) const {
  if (next_update_time == update_time) {
    return;
  }
  if (next_update_time < update_time) {
    throw std::runtime_error("Can't update Element to the past");
  }
  lt_time_t time_delta = next_update_time - update_time;
  cpu.update_commitment(time_delta, tau);
  memory.update_commitment(time_delta, tau);
  update_time = next_update_time;
}

lt_time_t Element::get_switch_time(const Element& other_element) const {
  if (other_element.update_time > update_time) {
    update(other_element.update_time);
  } else {
    other_element.update(update_time);
  }

  lt_time_t next_intersec = std::numeric_limits<lt_time_t>::infinity();

  auto update_intersec = [&next_intersec](lt_time_t intersec) {
    if (std::isfinite(intersec) && (intersec > 0) && 
        (intersec < next_intersec)) {
      next_intersec = intersec;
    }
  };

  update_intersec(calculate_intersec(cpu, other_element.cpu, other_element));
  update_intersec(calculate_intersec(cpu, other_element.memory, other_element));
  update_intersec(calculate_intersec(memory, other_element.cpu, other_element));
  update_intersec(calculate_intersec(memory, other_element.memory,
                                     other_element));
  if (std::isfinite(next_intersec)) {
    return next_intersec + update_time;
  }
  return std::numeric_limits<lt_time_t>::infinity();
}

lt_name_t Element::get_name() const {
  return name;
}

long double Element::get_cpu_commitment() const {
  return cpu.commitment;
}

long double Element::get_memory_commitment() const {
  return memory.commitment;
}

long double Element::get_priority() const {
  long double dominant_commitment = std::max(
    cpu.norm_commitment(), memory.norm_commitment());
  const Resource& dominant_resource = get_dominant_resource();

  return dominant_resource.norm_allocation() + dominant_commitment;
}

lt_time_t Element::get_update_time() const {
  return update_time;
}

long double Element::get_cpu_relative_allocation() const {
  return cpu.relative_allocation;
}

long double Element::get_memory_relative_allocation() const {
  return memory.relative_allocation;
}

void Element::set_cpu_relative_allocation(long double cpu_relative_allocation) {
  cpu.relative_allocation = cpu_relative_allocation;
}

void Element::set_memory_relative_allocation(long double memory_relative_allocation){
  memory.relative_allocation = memory_relative_allocation;
}

Element::operator std::string() const {
  std::ostringstream priority_out_stream;
  priority_out_stream << std::setprecision(50) << get_priority();
  return std::to_string(name) + "(" + priority_out_stream.str() + ")";
}

Element::Resource::Resource(long double system_total, long double commitment,
   long double relative_allocation, long double share)
   : system_total(system_total), commitment(commitment),
     relative_allocation(relative_allocation), share(share) { }

lt_time_t Element::calculate_intersec(const Element::Resource& my_res,
    const Element::Resource& other_res, const Element& other_element) const
{
  // overused resources
  long double ov1 = my_res.overused_resource() / my_res.system_total;
  long double ov2 = other_res.overused_resource() / other_res.system_total;
  
  // commitments
  long double c1 = my_res.norm_commitment();
  long double c2 = other_res.norm_commitment();

  // dominant allocations
  long double dom1 = get_dominant_resource().norm_allocation();
  long double dom2 = other_element.get_dominant_resource().norm_allocation();

  return tau * std::log((ov1 - ov2 + c2 - c1) / (ov1 - ov2 + dom1 - dom2));
}

long double Element::get_priority_derivative(lt_time_t time_delta) const {
  const Resource& dominant_resource = get_dominant_resource();
  return dominant_resource.commitment_derivative(time_delta, tau);
}

const Element::Resource& Element::get_dominant_resource() const {
  if (cpu.norm_allocation() > memory.norm_allocation()) {
    return cpu;
  }
  return memory;
}

long double Element::get_dominant_commitment() const {
  return std::max(cpu.norm_commitment(), memory.norm_commitment());
}

long double Element::Resource::norm_allocation() const {
  return relative_allocation / system_total;
}

long double Element::Resource::norm_commitment() const {
  return commitment / system_total;
}

long double Element::Resource::overused_resource() const {
  return std::max<long double>(relative_allocation - share, 0);
}

long double Element::Resource::commitment_derivative(lt_time_t time_delta,
    long double tau) const {
  return (overused_resource() / system_total - norm_commitment()) / 
         tau * std::exp(-time_delta/tau);
}

void Element::Resource::update_commitment(lt_time_t time_delta, long double tau)
const
{
  long double alpha = 1 - std::exp(-time_delta/tau);
  commitment += alpha * (overused_resource() - commitment);
}
