# -*- coding: utf-8 -*-
import numpy as np

from allocators.arrival import Arrival
from helpers.priority_queue import PriorityQueue


# arrival allocations are simpler, they just decide which task to run based on
# the jobs currently running

# the progressive filling algorithm, applied to DRF, increases every user
# dominant share at the same rate while increasing the other shares
# proportionally


# In practice each user could have a queue of tasks with different demands.
# However, for simplicity, here we keep only a single demand vector per user.
# Note this vector can be changed after the beginning.


class WDRF(Arrival):
    def __init__(self, capacities, weights, force=True):
        """
        :param capacities: array with capacities for each resource
        :param weights: each user's and resource weight
        :param demands: array with demands for each user [users]x[resources]
        :param force: when True, the allocation will not stop until there's no
        allocation demand that fits -- even if its user doesn't have the
        smallest dominant share.
        """
        super(WDRF, self).__init__(capacities, num_users=len(weights))
        self.weights = np.array(weights)
        self.dominant_share_queue = PriorityQueue(np.zeros(self.num_users))
        self.force = force
        self._hold_users = []  # keeps user when using "force"

    def _user_with_lowest_dominant_share(self):
        return self.dominant_share_queue.pop()

    def _insert_user(self, user):
        # we don't assume the user always has the same demand
        dominant_share = np.max(self.allocations[user] / self._capacities /
                                self.weights[user])
        self.dominant_share_queue.add(user, dominant_share)

    def _remove_user(self, user):
        self.dominant_share_queue.remove(user)

    def _unhold_users(self):
        for user in reversed(self._hold_users):
            self._insert_user(user)

    def pick_task(self):
        user = self._user_with_lowest_dominant_share()
        if user is None:
            return None

        def can_allocate_resource():
            if self.users_queues[user]:
                user_demand = self.users_queues[user][0].demands
                consumed_with_task = self.consumed_resources + user_demand
                return np.all(consumed_with_task <= self._capacities)
            return False

        if can_allocate_resource():
            self.run_after_task = lambda: self._insert_user(user)
            return self.users_queues[user].pop()
        elif self.force:
            self._hold_users.append(user)
            return self.pick_task()
        else:
            self._insert_user(user)
            return None

    def finish_task(self, user, task_demands, num_tasks=1):
        for _ in xrange(num_tasks):
            if self.consumed_resources < task_demands or \
               self.allocations[user] < task_demands:
                break
        self._remove_user(user)
        self._insert_user(user)
