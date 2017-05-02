# -*- coding: utf-8 -*-
import csv
from time import sleep

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
