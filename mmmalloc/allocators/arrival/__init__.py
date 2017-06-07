# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict, deque
import itertools

from mmmalloc.helpers.priority_queue import PriorityQueue


class Task(object):
    def __init__(self, user_id, task_id, start_time, finish_time, demands,
                 submit_time):
        self.user_id = user_id
        self.task_id = task_id
        self.user = Task._user_index[user_id]
        self.demands = np.array(demands)
        self.cpu = demands[0]
        self.memory = demands[1]
        self.submit_time = submit_time
        self.start_time = start_time
        self.finish_time = finish_time
        self.count = Task._counter.next()

    _counter = itertools.count()
    _user_index_generator = itertools.count()
    _user_index = defaultdict(_user_index_generator.next)

    def __hash__(self):
        return hash(self.count)

    def __eq__(self, other):
        if other is None:
            return False
        return self.count == other.count

    def __getitem__(self, key):
        return self.__dict__[key]  # gets KeyError exception when invalid

    @property
    def duration(self):
        return self.finish_time - self.start_time


# Simulates a task arrival process
# The simulate method takes a task generator, this task generator also controls
# the simulation pace -- events only happen when a task finishes or a task
# arrives. The time the system takes to make an allocation decision is
# considered negligible. Tasks that finished their execution are appended to
# the finished_tasks deque with the submit, start and finish times as well as
# the amount of CPU and memory used. This queue can be inspected after the
# simulation is complete or, even better, while it's still running.
class Arrival(object):
    def __init__(self, capacities, num_users, keep_history=False):
        self.num_resources = len(capacities)
        self.num_users = num_users
        self._capacities = np.array(capacities, dtype=float)
        self.consumed_resources = np.zeros(self.num_resources)
        self.allocations = np.zeros((self.num_users, self.num_resources))
        self.users_queues = defaultdict(deque)
        self.running_tasks = PriorityQueue()
        self.current_time = 0.0
        self.finished_tasks = deque()

        if keep_history:
            self.allocation_history = []
        else:
            self.allocation_history = None

    def pick_task(self):
        raise NotImplementedError()

    def _insert_user(self, user):
        raise NotImplementedError()

    def run_task(self):
        task = self.pick_task()
        if task is None:
            return False

        self.consumed_resources += task.demands
        self.allocations[task.user] += task.demands
        if self.allocation_history is not None:
            self.allocation_history.append(self.allocations.copy())
        task.finish_time = self.current_time + task.duration
        task.start_time = self.current_time
        self.running_tasks.add(task, task.finish_time)
        self._insert_user(task.user)
        return True

    def run_all_tasks(self):
        while self.run_task():
            pass

    def finish_task(self, task):
        raise NotImplementedError()

    def simulate(self, tasks, simulation_limit=None):
        if simulation_limit is None:
            simulation_limit = np.inf
        for task in tasks:
            if task.submit_time < self.current_time:
                raise RuntimeError('Task arrived in the future! Must provide '
                                   'tasks in chronological order.')
            if task.submit_time > simulation_limit:
                self._finish_tasks_until(simulation_limit)
                return
            if task.submit_time > self.current_time:
                self._finish_tasks_until(task.submit_time)
                self.current_time = task.submit_time
            self._insert_user(task.user)
            self.users_queues[task.user].append(task)
        self._finish_tasks_until(simulation_limit)

    def _finish_tasks_until(self, next_time):
        while True:
            self.run_all_tasks()
            next_task = self.running_tasks.get_min()
            if next_task is None or next_task.finish_time > next_time:
                break
            self.current_time = next_task.finish_time
            self.consumed_resources -= next_task.demands
            self.allocations[next_task.user] -= next_task.demands
            self.finished_tasks.append(self.running_tasks.pop())
            self.finish_task(next_task)

    def _pick_from_queue(self, queue, constraints=None):
        """
        If a user in the queue doesn't satisfy the constraints function we
        remove the user from the queue, if the constraints somehow change (i.e.
        user tasks finished) the user must be reinserted externally.
        """
        picked_task = None
        available_resource = self._capacities - self.consumed_resources

        # for some reason using np.all here was much slower...
        # this ugly solution using 2 returns performed way better
        def system_fulfills_request(demands):
            if demands[0] > available_resource[0]:
                return False
            return demands[1] <= available_resource[1]
            # return np.all(task.demands <= self._capacities)

        for user in queue.sorted_elements():
            if user is None:
                break

            if not self.users_queues[user]:
                queue.remove(user)
                continue

            task = self.users_queues[user][0]

            if constraints is None:
                pass_constraints = True
            else:
                pass_constraints = constraints(task)

            if pass_constraints and system_fulfills_request(task.demands):
                picked_task = self.users_queues[user].pop()
                break

            if not pass_constraints:
                queue.remove(user)

        return picked_task
