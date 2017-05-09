# -*- coding: utf-8 -*-
import threading
import pandas as pd
from tqdm import tqdm
from os import path

from allocators.arrival import Task
from allocators.arrival.wdrf import WDRF
from allocators.arrival.mmm_drf import MMMDRF
from helpers.file_name import FileName
from tasks import tasks_file_header, save_task_deque
from helpers.schema import SchemaIndex


def tasks_generator(tasks_df):
    task_index = SchemaIndex(tasks_file_header)
    for task_line in tqdm(tasks_df.itertuples(), total=len(tasks_df)):
        submit_time = task_line[task_index['submit_time']]
        user_index = task_line[task_index['user_id']]
        duration = task_line[task_index['finish_time']] - \
                   task_line[task_index['start_time']]
        demands = (task_line[task_index['cpu']],
                   task_line[task_index['memory']])
        task_id = task_line[task_index['task_id']]
        task = Task(user_index, task_id, duration, demands, submit_time)
        yield task


def wdrf(tasks_file, saving_dir, resource_percentage):
    #                     CPU     RAM    1000 users
    # allocator = WDRF([1528.0, 1346.0], [1]*1000)
    allocator = WDRF(system_resources, weights)

    saving_file = FileName('task_sim', 'wdrf', resource_percentage)
    saving_file = path.join(saving_dir, saving_file)

    simulate_task_allocation(allocator, tasks_file, saving_file)


def mmm_drf(tasks_file, saving_dir, resource_percentage, delta):
    # we may try to give 0 resources to all users at first
    allocator = MMMDRF(system_resources, users_resources, )

    saving_file = FileName('task_sim', '3mdrf', resource_percentage, delta)
    saving_file = path.join(saving_dir, saving_file)

    simulate_task_allocation(allocator, tasks_file, saving_file)


def simulate_task_allocation(allocator, tasks_file, saving_file):
    tasks_df = pd.read_csv(tasks_file, header=None, index_col=False,
                           names=tasks_file_header)
    tasks_df.sort_values('submit_time', inplace=True)

    done = threading.Event()
    saving_thread = threading.Thread(target=save_task_deque, args=(
        allocator.finished_tasks, saving_file, done))
    saving_thread.start()
    allocator.simulate(tasks_generator(tasks_df))
    done.set()
    saving_thread.join()
