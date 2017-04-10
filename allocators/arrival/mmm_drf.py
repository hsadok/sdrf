# -*- coding: utf-8 -*-
import heapq
import numpy as np

from allocators.arrival import Arrival


# 3M_DRF
# the 3M allocation must only come into action when users already reached 1/n
# of resource utilization for their dominant resource
# there must be a separate credibility for each resource and user
# We assume capacities and users_resources remain constant
class MMMDRF(Arrival):
    def __init__(self, capacities, users_resources, demands,
                 initial_credibilities=None):
        """
        :param capacities: array with capacities for each resource
        :param users_resources: array with users resources [users]x[resources]
        :param demands: array with demands for each user [users]x[resources]
        """
        super(MMMDRF, self).__init__(capacities, demands)
        self.user_resources = np.array(users_resources)

        self.user_resources_heap = [(0.0, u) for u in xrange(self.num_users)]
        heapq.heapify(self.user_resources_heap)

        if initial_credibilities is None:
            self.credibilities = np.zeros((self.num_users, self.num_resources))
        else:
            self.credibilities = np.array(initial_credibilities)

        self.user_credibilities_heap = [
            (c, i) for i, c in enumerate(np.max(self.credibilities, axis=1))]

        self.allocation_history = []
        self.queue_switch_time = -1

    def _insert_user_resources_heap(self, user):
        # same as wDRF when user_resources/capacities are used as the weight
        res_left = np.max(self.allocations[user]/self.user_resources[user])
        heapq.heappush(self.user_resources_heap, (res_left, user))

    def _insert_user_cred_heap(self, user):
        dominant_share = np.max((self.allocations[user] -
                                 self.user_resources[user] -
                                 self.credibilities[user]) / self._capacities)
        heapq.heappush(self.user_credibilities_heap, (dominant_share, user))

    def _allocate_from_queue(self, queue, insert_function, user_fulfilment):
        while len(queue) > 0:
            try:
                if not user_fulfilment:
                    print 'queue: ', queue
                dominant_share, user = heapq.heappop(queue)
            except IndexError:
                break

            user_demand = self._demands[user]
            user_allocation = self.allocations[user]

            system_fulfills_request = np.all(
                self.consumed_resources + user_demand <= self._capacities)

            if user_fulfilment:  # TODO HACK...
                user_fulfills_request = np.all(
                    user_allocation + user_demand <= self.user_resources)
            else:
                user_fulfills_request = True
                print 'user: ', user

            if system_fulfills_request and user_fulfills_request:
                self.consumed_resources += user_demand
                self.allocations[user] += user_demand
                insert_function(user)
                self.allocation_history.append(self.allocations.copy())
                return True

        return False

    def run_task(self):
        allocated = self._allocate_from_queue(self.user_resources_heap,
                                              self._insert_user_resources_heap,
                                              True)
        if not allocated:
            if self.queue_switch_time == -1:
                self.queue_switch_time = len(self.allocation_history)
                print 'switch allocations: ', self.allocations
            allocated = self._allocate_from_queue(self.user_credibilities_heap,
                                                  self._insert_user_cred_heap,
                                                  False)
        return allocated












    def set_user_demand(self, user, demand):
        # self._demands[user] = demand
        # self._remove_user(user)
        # if np.any(demand):  # nonzero demand for the user
        #     self._insert_user(user)
        # TODO
        pass

    def update(self, user):
        # TODO
        pass

    def finish_task(self, user, task_demands, num_tasks=1):
        # TODO
        self.update(user)

        pass

# Regime 1 - "private usage"
# * keep track of the minimum difference between user usage and the resources
#   they possess in proportion to the total amount of the resource.
# * allocate resource from users whose minimum difference is the greatest (this
#   can be implemented using a priority queue of minimum differences). The
#   resource with the minimum difference may not be the user dominant resource!
# * as soon as a user reaches a point where they need more resources than they
#   possess they enter the next regime.

# Regime 2 - "3M"
# Wait till all users with pending tasks are in the 2nd regime
# Give priority to whoever has the greatest smallest credibility share!
# smallest credibility share for user i:
#     min(credibility_vector_i/capacity_vector_i)
# ?? if we keep allocating beyond negative credibility does it work?

# Regime 3 - "pure DRF"
# If all users have their smallest credibility share zero (it can actually be
# greater than zero, as long as it is insufficient for a single task), apply
# DRF.

# ===== Credibility =====
# -- Updating --
# We update the credibility everytime a task finishes.
# What and how to update? Some ideas:
# * Every time a task finishes, the user whose task finished should have their
#   credibility discounted -- maybe this is not the best time...
# * Whenever a task enters the queue -- if a user submit a lot of tasks this
# gets really outdated, so not a good idea.
# . NOTE: something to consider is that if a user is in the first regime their
# credibility can only improve, they're also not competing with the other
# users, in a credibility standpoint, every task they have is attended as soon
# as possible.
#
# -- Amortization --
# I'll implement first without amortizing the credibility. However this should
# be done at some point. The question that pops right away is: Doesn't amortize
# all credibilities require us to update all users in the queue? In fact it
# doesn't! Instead of amortizing every user credibility we multiply whatever
# updated credibility proportionally so that it virtually discounts everything
# else. Note that the actual credibility is still required but it can be
# recovered using the same factor used to multiply the credibility when it
# enters the queue.

# ===== draft =====
# * If the credibility(positive)-allocation > 0

# For a single resource we would have to allocate whoever has the best
# credibility (discount the user and reinsert).
#
# For more resources we get inspiration from DRF

#
# Now allocate resources considering users's credibility instead of their
# possesses using the same strategy as before.
# * As soon as a user reaches a point where they need more resources than their
# credibility+possesses allow

# Regime

# Note:
# this procedure should be exactly equal to DRF when all users possess the same
# amount of resources and have zero credibility
