# -*- coding: utf-8 -*-
import threading
from Queue import Queue
import pandas as pd
from tqdm import tqdm
from os import path

from mmmalloc.allocators.arrival import Task
from mmmalloc.allocators.arrival.wdrf import WDRF
from mmmalloc.allocators.arrival.mmm_drf import MMMDRF
from mmmalloc.helpers import get_line_number
from mmmalloc.helpers.file_name import FileName
from mmmalloc.helpers.schema import SchemaIndex
from mmmalloc.tasks import tasks_file_header, save_task_deque
from mmmalloc.tasks.system_utilization import SystemUtilization


def file_loader(file_name, out_queue):
    chunk_size = out_queue.maxsize
    if out_queue.maxsize == 0:
        chunk_size = None  # read the entire thing at once
    csv_reader = pd.read_csv(file_name, header=None, index_col=False,
                             chunksize=chunk_size, names=tasks_file_header)
    task_index = SchemaIndex(tasks_file_header)
    for df in csv_reader:
        for task_line in df.itertuples():
            submit_time = task_line[task_index['submit_time']]
            user_index = task_line[task_index['user_id']]
            duration = task_line[task_index['finish_time']] - \
                       task_line[task_index['start_time']]
            demands = (task_line[task_index['cpu']],
                       task_line[task_index['memory']])
            task_id = task_line[task_index['task_id']]
            task = Task(user_index, task_id, duration, demands, submit_time)
            out_queue.put(task)
    out_queue.put(None)


def tasks_generator(sorted_tasks_file):
    line_queue = Queue(10000)

    loading_thread = threading.Thread(target=file_loader,
                                      args=(sorted_tasks_file, line_queue))
    loading_thread.start()

    last_submit_time = 0
    num_tasks = get_line_number(sorted_tasks_file)
    for task in tqdm(iter(line_queue.get, None), total=num_tasks):
        if task.submit_time < last_submit_time:
            raise RuntimeError('Not sorted! %f < %f' % (task.submit_time,
                                                        last_submit_time))
        last_submit_time = task.submit_time
        yield task


# def wdrf(system_resources, resource_percentage, saving_dir, tasks_file,
# weights):
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


# def mmm_drf(system_resources, users_resources, resource_percentage,
# saving_dir, tasks_file):
def mmm_drf(tasks_file, saving_dir, resource_percentage, delta):
    print 'resource percentage: ', resource_percentage
    system_utilization = SystemUtilization(tasks_file)
    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]

    users_resources_dict = {}

    for user in system_utilization.users_cpu_mean.keys():
        users_resources_dict[user] = [
            system_utilization.users_cpu_mean[user] * resource_percentage,
            system_utilization.users_memory_mean[user] * resource_percentage
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
