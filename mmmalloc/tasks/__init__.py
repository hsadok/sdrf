# -*- coding: utf-8 -*-
import csv
import threading
from Queue import Queue
from time import sleep

import pandas as pd
from tqdm import tqdm

from mmmalloc.allocators.arrival import Task
from mmmalloc.helpers import get_line_number
from mmmalloc.helpers.schema import SchemaIndex

tasks_file_header = ['submit_time', 'start_time', 'finish_time', 'user_id',
                     'task_id', 'cpu', 'memory']


def save_task_deque(task_deque, saving_file, done=None):
    def save_max():
        f = open(saving_file, 'a')
        wr = csv.writer(f)
        while len(task_deque) > 0:
            task = task_deque.pop()
            wr.writerow([task[i] for i in tasks_file_header])

    if done is not None:
        while not done.is_set():
            save_max()
            sleep(1)
    save_max()


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


def tasks_generator(tasks_file):
    line_queue = Queue(10000)
    loading_thread = threading.Thread(target=file_loader,
                                      args=(tasks_file, line_queue))
    loading_thread.start()
    num_tasks = get_line_number(tasks_file)
    for task in tqdm(iter(line_queue.get, None), total=num_tasks):
        yield task
