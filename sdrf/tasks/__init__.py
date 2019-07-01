# -*- coding: utf-8 -*-
import csv
import threading
from Queue import Queue
from time import sleep
import os
import pandas as pd
from tqdm import tqdm

from sdrf.allocators import Task
from sdrf.helpers import get_line_number
from sdrf.helpers.schema import SchemaIndex

tasks_file_header = ['submit_time', 'start_time', 'finish_time', 'user_id',
                     'task_id', 'cpu', 'memory']
jobs_file_header = ['job_id', 'user_id', 'submit_time', 'start_time',
                    'finish_time', 'duration', 'num_tasks', 'cpu_mean',
                    'memory_mean']


def save_from_deque(task_deque, saving_file, header, done=None,
                    write_header=False):
    try:
        os.remove(saving_file)
    except OSError:
        pass

    if write_header:
        with open(saving_file, 'w') as f:
            wr = csv.writer(f)
            wr.writerow(header)

    def save_max():
        f = open(saving_file, 'a')
        wr = csv.writer(f)
        while len(task_deque) > 0:
            task = task_deque.popleft()
            wr.writerow([task[i] for i in header])

    if done is not None:
        while not done.is_set():
            save_max()
            sleep(1)
    save_max()


def file_loader(file_name, out_queue, stop_time=None, truncate=False):
    """
    Loads tasks file adding each task to the queue
    :param file_name: tasks file name
    :param out_queue: tasks will be appended to this queue
    :param stop_time: (optional) when this is provided, tasks that start after
    this time will not be loaded to the queue.
    :param truncate: (optional) truncate tasks if stop_time is provided
    """
    chunk_size = out_queue.maxsize
    if out_queue.maxsize == 0:
        chunk_size = None  # read the entire thing at once
    csv_reader = pd.read_csv(file_name, header=None, index_col=False,
                             chunksize=chunk_size, names=tasks_file_header)
    task_index = SchemaIndex(tasks_file_header)
    for df in csv_reader:
        for task_line in df.itertuples():
            submit_time = task_line[task_index['submit_time']]
            start_time = task_line[task_index['start_time']]
            finish_time = task_line[task_index['finish_time']]

            if stop_time is not None:
                if start_time > stop_time:
                    continue
                if truncate and (finish_time > stop_time):
                    finish_time = stop_time

            user_index = task_line[task_index['user_id']]
            demands = (task_line[task_index['cpu']],
                       task_line[task_index['memory']])
            task_id = task_line[task_index['task_id']]
            task = Task(user_index, task_id, start_time, finish_time, demands,
                        submit_time)
            out_queue.put(task)
    out_queue.put(None)


def tasks_generator(tasks_file, stop_time=None, truncate=False):
    line_queue = Queue(10000)
    loading_thread = threading.Thread(target=file_loader,
                                      args=(tasks_file, line_queue, stop_time,
                                            truncate))
    loading_thread.start()
    task_counter = 0
    num_tasks = get_line_number(tasks_file)
    last_percentage = -1
    for task in iter(line_queue.get, None):
        task_counter += 1
        percentage = task_counter * 100 / num_tasks
        if percentage > last_percentage:
            last_percentage = percentage
            print percentage, '%'
        yield task

    # for task in tqdm(iter(line_queue.get, None), total=num_tasks):
    #     yield task
