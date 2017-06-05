# -*- coding: utf-8 -*-
import threading
import pandas as pd
from tqdm import tqdm
from os import path
import numpy as np; np.seterr(all='raise')

from mmmalloc.allocators.arrival import Task
from mmmalloc.allocators.arrival.wdrf import WDRF
from mmmalloc.allocators.arrival.mmm_drf import MMMDRF
from mmmalloc.helpers import get_line_number
from mmmalloc.helpers.file_name import FileName
from mmmalloc.tasks import tasks_file_header, save_task_deque
from mmmalloc.tasks.system_utilization import SystemUtilization


def tasks_generator(sorted_tasks_file):
    csv_reader = pd.read_csv(sorted_tasks_file, header=None, index_col=False,
                             chunksize=1, names=tasks_file_header)
    last_submit_time = 0
    for line in tqdm(csv_reader, total=get_line_number(sorted_tasks_file)):
        submit_time = line['submit_time'].values[0]
        if submit_time < last_submit_time:
            raise RuntimeError('Not sorted! %f < %f' % (submit_time,
                                                        last_submit_time))
        last_submit_time = submit_time
        user_index = line['user_id'].values[0]
        duration = line['finish_time'].values[0] - line['start_time'].values[0]
        demands = (line['cpu'].values[0], line['memory'].values[0])
        task_id = line['task_id'].values[0]
        task = Task(user_index, task_id, duration, demands, submit_time)
        yield task


# def wdrf(system_resources, resource_percentage, saving_dir, tasks_file, weights):
def wdrf(tasks_file, saving_dir, resource_percentage, weights=None):
    system_utilization = SystemUtilization(tasks_file)

    if weights is None:
        weights = [1] * system_utilization.num_users

    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]
    allocator = WDRF(system_resources, weights)

    saving_file = FileName('task_sim', 'wdrf', resource_percentage)
    saving_file = path.join(saving_dir, saving_file.name)

    simulate_task_allocation(allocator, tasks_file, saving_file)


# def mmm_drf(system_resources, users_resources, resource_percentage, saving_dir,
#             tasks_file):
def mmm_drf(tasks_file, saving_dir, resource_percentage, delta):
    print 'resource percentage: ', resource_percentage
    system_utilization = SystemUtilization(tasks_file)
    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]

    users_resources_dict = {}

    for user in system_utilization._users_cpu_mean.keys():
        users_resources_dict[user] = [
            system_utilization._users_cpu_mean[user] * resource_percentage,
            system_utilization._users_memory_mean[user] * resource_percentage
        ]

    allocator = MMMDRF(system_resources, users_resources_dict, delta=delta)

    saving_file = FileName('task_sim', '3mdrf', resource_percentage)
    saving_file = path.join(saving_dir, saving_file.name)

    simulate_task_allocation(allocator, tasks_file, saving_file)


def simulate_task_allocation(allocator, tasks_file, saving_file):
    done = threading.Event()
    saving_thread = threading.Thread(target=save_task_deque, args=(
        allocator.finished_tasks, saving_file, done))
    saving_thread.start()
    allocator.simulate(tasks_generator(tasks_file))
    done.set()
    saving_thread.join()
