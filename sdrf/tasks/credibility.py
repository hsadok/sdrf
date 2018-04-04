# coding=utf-8
# credibility.py
# 2017, all rights reserved
import threading
from math import exp, log
from collections import deque

from tqdm import tqdm

from sdrf.allocators.arrival.mmm_drf import time_scale_multiplier
from sdrf.helpers.file_name import FileName
from sdrf.tasks import tasks_generator, save_from_deque
from sdrf.tasks.system_utilization import SystemUtilization


def credibility_summary(tasks_file, original_dataset, saving_file):
    file_att = FileName(tasks_file)
    delta = file_att.delta
    resource_percentage = file_att.resource_percentage
    same_share = file_att.same_share
    system_utilization = SystemUtilization(original_dataset)
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
    if same_share:
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
    saving_deque = deque()
    title_row = ['time']
    for user in xrange(num_users):
        user_id = user_id_map[user]
        title_row.append(user_id + '-cpu')
        title_row.append(user_id + '-memory')

    users_cpu_allocation = num_users * [0.0]
    users_memory_allocation = num_users * [0.0]
    prev_creds_cpu = num_users * [0.0]
    prev_creds_memory = num_users * [0.0]
    prev_time = first_event[0]

    users_cpu_allocation[first_event[3]] = first_event[1]
    users_memory_allocation[first_event[3]] = first_event[2]

    done = threading.Event()
    saving_thread = threading.Thread(target=save_from_deque, args=(
        saving_deque, saving_file, title_row, done, True))
    saving_thread.start()

    print 'processing events'
    for event in tqdm(events):
        event_time = event[0]
        cpu = event[1]
        memory = event[2]
        event_user = event[3]
        time_delta = event_time - prev_time
        if time_delta != 0:
            if tau == 0:
                alpha = 1
            else:
                alpha = 1 - exp(-time_delta / tau)
            instant_dict = {'time': event_time}
            prev_time = event_time
            for user in xrange(num_users):
                user_id = user_id_map[user]
                prev_cred = prev_creds_cpu[user]
                new_cred = prev_cred + alpha * (users_cpu_allocation[user] -
                                                owned_cpu[user] - prev_cred)
                instant_dict[user_id + '-cpu'] = new_cred
                prev_creds_cpu[user] = new_cred

                prev_cred = prev_creds_memory[user]
                new_cred = prev_cred + alpha * (users_memory_allocation[user] -
                                                owned_memory[user] - prev_cred)
                instant_dict[user_id + '-memory'] = new_cred
                prev_creds_memory[user] = new_cred
            saving_deque.append(instant_dict)

        users_cpu_allocation[event_user] += cpu
        users_memory_allocation[event_user] += memory

    done.set()
    saving_thread.join()
