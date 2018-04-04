# -*- coding: utf-8 -*-
import threading
from collections import deque
import numpy as np

from sdrf.tasks import save_from_deque, tasks_file_header
from sdrf.helpers.schema import Schema, SchemaIndex
from sdrf.helpers.task_events import task_events


def filter_tasks(dataset_dir, saving_file):
    task_states = {}
    running_tasks = {}
    ignored_events = 0
    complete_tasks = deque()
    done = threading.Event()
    index = SchemaIndex(Schema(dataset_dir).task_events)

    saving_thread = threading.Thread(target=save_from_deque, args=(
        complete_tasks, saving_file, tasks_file_header, done))
    saving_thread.start()

    for event in task_events(dataset_dir, progress=True):
        missing_info_empty = np.isnan(event[index['missing info']])
        if not missing_info_empty:
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
                # Some tasks have 0 cpu or 0 memory, we are ignoring those
                if (task_info['cpu'] > 0) and (task_info['memory'] > 0):
                    complete_tasks.append(task_info)
                del task_states[task_id]
                del running_tasks[task_id]

    print 'ignored events: ', ignored_events
    done.set()
    saving_thread.join()
