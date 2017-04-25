# -*- coding: utf-8 -*-
import threading
import csv
from collections import deque
from time import sleep
import numpy as np

from helpers.schema import Schema, SchemaIndex
from helpers.task_events import task_events

header = ['submit_time', 'start_time', 'finish_time', 'user_id', 'task_id',
          'cpu', 'memory', 'disk']


class FilterTasks(object):
    def __init__(self, dataset_dir, saving_file):
        self.complete_tasks = deque()
        self.done = threading.Event()
        self.dataset_dir = dataset_dir
        self.saving_file = saving_file

    def save(self):
        def save_max():
            f = open(self.saving_file, 'a')
            wr = csv.writer(f)
            while len(self.complete_tasks) > 0:
                task = self.complete_tasks.pop()
                wr.writerow([task[i] for i in header])

        while not self.done.is_set():
            save_max()
            sleep(1)
        save_max()

    def filter_tasks(self):
        task_states = {}
        running_tasks = {}
        ignored_events = 0
        index = SchemaIndex(Schema(self.dataset_dir).task_events)

        saving_thread = threading.Thread(target=self.save)
        saving_thread.start()

        for event in task_events(self.dataset_dir, progress=True):
            missing_info = np.isnan(event[index['missing info']])
            if not missing_info:
                ignored_events += 1
                continue

            job_id = event[index['job ID']]
            task_index = event[index['task index']]
            task_id = str(job_id) + '-' + str(task_index)

            state = task_states.get(task_id, '')
            event_type = event[index['event type']]
            if event_type == 0:  # SUBMIT
                submit_time = event[index['time']]
                if submit_time != 0:  # started before the dataset beginning
                    task_states[task_id] = 'PENDING'
                    running_tasks[task_id] = {'user_id': event[index['user']],
                                              'submit_time': submit_time}
            elif event_type == 1:  # SCHEDULE
                if state == 'PENDING':
                    task_states[task_id] = 'RUNNING'
                    running_tasks[task_id].update({
                        'start_time': event[index['time']],
                        'cpu': event[index['CPU request']],
                        'memory': event[index['memory request']],
                        'disk': event[index['disk space request']]
                    })
            elif event_type in [2, 5, 6]:  # EVICT, KILL or LOST
                if state != '':
                    del task_states[task_id]
                    del running_tasks[task_id]
            elif event_type == 3 and state == 'PENDING':  # FAIL while PENDING
                del task_states[task_id]
                del running_tasks[task_id]
            elif event_type in [3, 4]:  # FAIL or FINISH
                if state == 'RUNNING':
                    task_info = running_tasks[task_id]
                    task_info.update({'task_id': task_id,
                                      'finish_time': event[index['time']]})
                    self.complete_tasks.append(task_info)
                    del task_states[task_id]
                    del running_tasks[task_id]

        print 'ignored events: ', ignored_events
        self.done.set()
        saving_thread.join()
