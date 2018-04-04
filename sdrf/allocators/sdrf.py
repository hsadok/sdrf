# -*- coding: utf-8 -*-
import numpy as np
from math import log

from sdrf.allocators import Arrival, Task
from sdrf.helpers.priority_queue import PriorityQueue

from sdrf.helpers.live_tree import LiveTree, \
    Element


# Using those indexes make stuff less generic, but generality was kinda
# compromised already when I designed the LiveTree considering only
# cpu and memory  ¯\_(ツ)_/¯
cpu_index = 0
memory_index = 1

time_scale_multiplier = 1e6  # using seconds
# time_scale_multiplier = 1000  # using milliseconds


# SDRF
# the SDRF allocation must only come into action when users already reached 1/n
# of resource utilization for their dominant resource
# there must be a separate credibility for each resource and user
class SDRF(Arrival):
    def __init__(self, capacities, users_resources_dict, delta, start_time,
                 initial_credibilities=None, keep_history=False):
        """
        :param capacities: array with capacities for each resource
        :param users_resources_dict: dict with users resources user:[resources]
        """
        num_users = len(users_resources_dict)

        super(SDRF, self).__init__(capacities, num_users, keep_history)

        self.current_time = start_time

        users_resources = [0]*num_users
        for user, resource in users_resources_dict.iteritems():
            users_resources[Task._user_index[user]] = resource  # HACK!

        self._user_resources = np.array(users_resources)
        self.delta = delta
        if delta == 0:
            self.tau = 0
        else:
            self.tau = -1.0 * time_scale_multiplier/log(delta)

        if initial_credibilities is None:
            credibilities = np.zeros((self.num_users, self.num_resources))
        else:
            credibilities = np.array(initial_credibilities)

        self.idle_users = {}
        for user in xrange(num_users):
            cpu_relativ = - self._user_resources[user][cpu_index]
            mem_relativ = - self._user_resources[user][memory_index]
            system_cpu = self._capacities[cpu_index]
            system_mem = self._capacities[memory_index]
            cred_cpu = credibilities[user][cpu_index]
            cred_mem = credibilities[user][memory_index]
            cpu_share = system_cpu / num_users
            mem_share = system_mem / num_users

            # in the beginning all users are idle
            self.idle_users[user] = Element(user, self.current_time, self.tau,
                                            system_cpu, cred_cpu, cpu_relativ,
                                            cpu_share, system_mem, cred_mem,
                                            mem_relativ, mem_share)

        self.user_credibilities_queue = QueueProxy(self)

    def _insert_user(self, user):
        cpu_relative_allocation = self.allocations[user][cpu_index] - \
                                  self._user_resources[user][cpu_index]
        memory_relative_allocation = self.allocations[user][memory_index] - \
                                     self._user_resources[user][memory_index]
        self.user_credibilities_queue.add(user, cpu_relative_allocation,
                                          memory_relative_allocation)

    def pick_task(self):
        return self._pick_from_queue(self.user_credibilities_queue)

    def finish_task(self, task):
        # When we reinsert the user there are basically 2 possibilities: The
        # first is when the user is idle, when we reinsert, their credibility
        # will be updated. The second is when the user is not idle (already in
        # the queue), by calling _insert_user the user is removed and
        # reinserted with the new credibility
        self._insert_user(task.user)

    def print_stats(self, extra_info=None):
        info_dict = {
            'delta': self.delta,
            'capacities': list(self._capacities)
        }
        if extra_info is not None:
            info_dict['extra_info'] = extra_info
        QueueProxy.print_stats('time_stats.txt', info_dict)
        print 'credibilities: '
        for u in self.idle_users.values():
            print 'cpu: ',  u.cpu_credibility, 'memory: ', u.memory_credibility


class ReservedSDRF(SDRF):
    def __init__(self, capacities, users_resources_dict, delta, start_time,
                 initial_credibilities=None, keep_history=False):
        """
        :param capacities: array with capacities for each resource
        :param users_resources_dict: dict with users resources user:[resources]
        """
        super(ReservedSDRF, self).__init__(capacities, users_resources_dict,
                                            delta, start_time,
                                            initial_credibilities,
                                            keep_history)

        self._user_resources_queue = PriorityQueue(np.zeros(self.num_users))

    def _insert_user_resources_heap(self, user):
        # same as wDRF when user_resources/capacities are used as the weight
        res_left = np.max(self.allocations[user] / self._user_resources[user])

        # don't bother adding when users are using more than they have (their
        # share is >= 1)
        if res_left < 1:
            self._user_resources_queue.add(user, res_left)

    def _insert_user(self, user):
        self._insert_user_resources_heap(user)
        super(ReservedSDRF, self)._insert_user(user)

    def pick_task(self):
        def user_fulfills_request(task):
            user_alloc = self.allocations[task.user]
            return np.all((user_alloc + task.demands)
                          <= self._user_resources[task.user])

        picked_task = self._pick_from_queue(self._user_resources_queue,
                                            user_fulfills_request)
        if self._system_full:
            return None

        if picked_task is None:
            picked_task = super(ReservedSDRF, self).pick_task()

        return picked_task


# This class has 2 main purposes, to make sure the credibility remains up to
# date when the user is removed and to guarantee that only the name goes out
class QueueProxy(LiveTree):
    def __init__(self, sdrf_obj):
        super(QueueProxy, self).__init__()
        self.sdrf_obj = sdrf_obj

    def sorted_elements(self):
        self.update()
        return (e.name for e in super(QueueProxy, self).sorted_elements())

    def add(self, user_name, cpu_relative_alloc, memory_relative_alloc):
        if user_name in self:
            self.remove(user_name)

        element = self.sdrf_obj.idle_users[user_name]
        element.update(self.sdrf_obj.current_time)

        element.cpu_relative_allocation = cpu_relative_alloc
        element.memory_relative_allocation = memory_relative_alloc

        super(QueueProxy, self).add(element)

    def update(self, current_time=None):
        if current_time is None:
            current_time = self.sdrf_obj.current_time
        super(QueueProxy, self).update(current_time)

    def get_min(self, current_time=None):
        if current_time is None:
            current_time = self.sdrf_obj.current_time
        return super(QueueProxy, self).get_min(current_time).name

    def pop(self, current_time=None):
        if current_time is None:
            current_time = self.sdrf_obj.current_time
        element = super(QueueProxy, self).pop(current_time)
        self._idle_element(element)
        return element.name

    def remove(self, name):
        removed_element = super(QueueProxy, self).remove(name)
        self._idle_element(removed_element)

    def _idle_element(self, element):
        element.update(self.sdrf_obj.current_time)
        self.sdrf_obj.idle_users[element.name] = element
