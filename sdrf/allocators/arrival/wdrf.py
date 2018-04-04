# -*- coding: utf-8 -*-
import numpy as np

from sdrf.allocators.arrival import Arrival, Task
from sdrf.helpers.priority_queue import PriorityQueue


# arrival allocations are simpler, they just decide which task to run based on
# the jobs currently running
#
# the progressive filling algorithm, applied to DRF, increases every user
# dominant share at the same rate while increasing the other shares
# proportionally

class WDRF(Arrival):
    def __init__(self, capacities, num_users, users_weights_dict=None,
                 keep_history=False):
        """
        :param capacities: array with system capacities for each resource
        :param weights: each user's resources weight
        """
        super(WDRF, self).__init__(capacities, num_users, keep_history)

        weights = [[1, 1]] * num_users
        if users_weights_dict is not None:
            for user, weight in users_weights_dict.iteritems():
                weights[Task._user_index[user]] = weight  # HACK!

        self.weights = np.array(weights)
        self.dominant_share_queue = PriorityQueue()

    def _insert_user(self, user):
        dominant_share = np.max(self.allocations[user] / self._capacities /
                                self.weights[user])
        self.dominant_share_queue.add(user, dominant_share)

    def pick_task(self):
        return self._pick_from_queue(self.dominant_share_queue)

    def finish_task(self, task):
        self._insert_user(task.user)
