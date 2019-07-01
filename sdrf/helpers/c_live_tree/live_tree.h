//
// Live Tree
// Priority Queue with weights that change overtime in a predictive way
//

#ifndef LIVE_TREE_H
#define LIVE_TREE_H

#include <string>
#include <forward_list>
#include <set>
#include <map>
#include <vector>

#include "element.h"


/*
 * Every element in the tree checks if in the future they are going to
 * be switched with their right neighbor. If this is the case they calculate
 * when this is going to happen and add an event to the events set
 */
class LiveTree {
 public:
  typedef std::set<std::pair<lt_time_t, lt_name_t>> events_set; //time, name
  typedef std::map<Element, events_set::iterator> elements_map; //element, event
  typedef std::vector<elements_map::iterator> elements_name_map;

  LiveTree();
  void add(const Element element);
  Element pop(lt_time_t current_time);
  Element get_min(lt_time_t current_time);
  elements_map::const_iterator cbegin();
  elements_map::const_iterator cend();
  Element remove(const lt_name_t& name);
  bool empty() const;
  bool element_is_in(const lt_name_t& name) const;
  operator std::string() const;
  void update(lt_time_t current_time);

  static int get_insert_count();
  static int get_update_count();
  static int get_events_count();

 private:
  lt_time_t last_time;
  events_set events;
  elements_map elements_priority; // sort elements and also link to events
  elements_name_map elements_name_mapper;

  static int insert_count;
  static int update_count;
  static int events_count;

  void update_event(elements_map::iterator iter);
  void check_order() const;
  void print_info() const;
};

#endif // LIVE_TREE_H
