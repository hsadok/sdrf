# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict, deque
import itertools

from helpers.priority_queue import PriorityQueue


class Task(object):
    def __init__(self, user, finish_time, demands):
        self.user = user
        self.finish_time = finish_time
        self.demands = demands
        self.count = Task._counter.next()

    _counter = itertools.count()

    def __hash__(self):
        return hash(self.count)

    def __eq__(self, other):
        return self.count == other.count


class Arrival(object):
    def __init__(self, capacities, demands):
        self.num_resources = len(capacities)
        self.num_users = len(demands)
        self._capacities = np.array(capacities)
        self._demands = np.array(demands)
        self.consumed_resources = np.zeros(self.num_resources)
        self.allocations = np.zeros((self.num_users, self.num_resources))
        self.users_queues = defaultdict(deque)
        self.running_tasks = PriorityQueue()
        self.current_time = 0.0

        self.allocation_history = []

    def pick_task(self):
        raise NotImplementedError()

    def run_task(self):
        task = self.pick_task()
        if task is None:
            return False

        self.consumed_resources += task.demands
        self.allocations[task.user] += task.demands
        self.allocation_history.append(self.allocations.copy())
        self.running_tasks.add(task, task.finish_time)
        return True

    def run_all_tasks(self):
        while self.run_task():
            pass

    def set_user_demand(self, user, demand):
        self._demands[user] = demand

    def finish_task(self, user, task_demands, num_tasks=1):
        raise NotImplementedError()

    def add_to_queue(self, user, submit_time, duration, task_demands):
        while True:
            next_task = self.running_tasks.get_min()
            if next_task is None or next_task.finish_time > submit_time:
                break

            self.finish_task(next_task.user, next_task.demands)
            self.running_tasks.pop()

        self.users_queues[user].append((duration, task_demands))
        # termination queue

    @property
    def _duration(self):  # TODO get actual duration
        return defaultdict(float)
