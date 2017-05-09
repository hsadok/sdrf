# -*- coding: utf-8 -*-
import numpy as np

from allocators.arrival import Arrival
from helpers.priority_queue import PriorityQueue


# arrival allocations are simpler, they just decide which task to run based on
# the jobs currently running
#
# the progressive filling algorithm, applied to DRF, increases every user
# dominant share at the same rate while increasing the other shares
# proportionally

class WDRF(Arrival):
    def __init__(self, capacities, weights, keep_history=False):
        """
        :param capacities: array with capacities for each resource
        :param weights: each user's resources weight
        """
        super(WDRF, self).__init__(capacities, len(weights), keep_history)
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
