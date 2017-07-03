# coding=utf-8
# credibility.py
# 2017, all rights reserved
import csv
from math import exp, log
from collections import deque

from mmmalloc.allocators.arrival.mmm_drf import time_scale_multiplier
from mmmalloc.helpers.file_name import FileName
from mmmalloc.tasks import tasks_generator
from mmmalloc.tasks.system_utilization import SystemUtilization


def credibility_summary(tasks_file, saving_file):
    file_att = FileName(tasks_file)
    delta = file_att.delta
    resource_percentage = file_att.resource_percentage
    system_utilization = SystemUtilization(tasks_file)
    user_id_map = {}

    print 'delta: ', delta
    if delta == 0:
        tau = 0.0
    else:
        tau = -1.0 * time_scale_multiplier / log(delta)

    events = deque()

    for task in tasks_generator(tasks_file):
        events.append((task.start_time, task.cpu, task.memory, task.user))
        events.append((task.finish_time, -task.cpu, -task.memory, task.user))
        user_id_map[task.user] = task.user_id

    num_users = len(user_id_map)
    owned_cpu = [0.0] * num_users
    owned_memory = [0.0] * num_users
    if 'same_share' in tasks_file:
        print 'same share'
    else:
        for user in xrange(num_users):
            user_id = user_id_map[user]
            owned_cpu[user] = resource_percentage * \
                              system_utilization.users_cpu_mean[user_id]
            owned_memory[user] = resource_percentage * \
                                 system_utilization.users_memory_mean[user_id]

    events = sorted(events)

    first_event = events.pop(0)
    aggregated_time = deque([first_event[0]])
    users_cpu_allocation = num_users * [0.0]
    users_cpu_allocation[first_event[3]] = first_event[1]
    users_memory_allocation = num_users * [0.0]
    users_memory_allocation[first_event[3]] = first_event[2]
    users_cpu_credibility = [deque([0.0]) for _ in xrange(num_users)]
    users_memory_credibility = [deque([0.0]) for _ in xrange(num_users)]

    for event in events:
        event_time = event[0]
        cpu = event[1]
        memory = event[2]
        event_user = event[3]
        time_delta = event_time - aggregated_time[-1]
        if time_delta != 0:
            if tau == 0:
                alpha = 1
            else:
                alpha = 1 - exp(-time_delta / tau)
            for user in xrange(num_users):
                prev_cred = users_cpu_credibility[user][-1]
                new_cred = prev_cred + alpha * (users_cpu_allocation[user] -
                                                owned_cpu[user] - prev_cred)
                users_cpu_credibility[user].append(new_cred)
                prev_cred = users_memory_credibility[user][-1]
                new_cred = prev_cred + alpha * (users_memory_allocation[user] -
                                                owned_memory[user] - prev_cred)
                users_memory_credibility[user].append(new_cred)
            aggregated_time.append(event_time)

        users_cpu_allocation[event_user] += cpu
        users_memory_allocation[event_user] += memory

    print 'saving...'

    with open(saving_file, 'wb') as f:
        wr = csv.writer(f)
        title_row = ['time']
        for user in xrange(num_users):
            user_id = user_id_map[user]
            title_row.append(user_id + '-cpu')
            title_row.append(user_id + '-memory')
        wr.writerow(title_row)
        while aggregated_time:
            row = list()
            row.append(aggregated_time.popleft())
            for user in xrange(num_users):
                row.append(users_cpu_credibility[user].popleft())
                row.append(users_memory_credibility[user].popleft())
            wr.writerow(row)
