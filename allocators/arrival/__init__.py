# -*- coding: utf-8 -*-
import numpy as np


class Arrival(object):
    def __init__(self, capacities, demands):
        self.num_resources = len(capacities)
        self.num_users = len(demands)
        self._capacities = np.array(capacities)
        self._demands = np.array(demands)
        self.consumed_resources = np.zeros(self.num_resources)
        self.allocations = np.zeros((self.num_users, self.num_resources))

    def run_task(self):
        raise NotImplementedError()

    def run_all_tasks(self):
        while self.run_task():
            pass

    def set_user_demand(self, user, demand):
        self._demands[user] = demand

    def finish_task(self, user, task_demands, num_tasks=1):
        raise NotImplementedError()


def remove_user_from_queue(user, queue):
    queue[:] = [i for i in queue if i[1] != user]
