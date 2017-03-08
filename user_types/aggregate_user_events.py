import csv
from os import path, listdir
import pandas as pd
from collections import defaultdict, deque
from helpers.schema import Schema
import numpy as np
import threading
import itertools
import time


def event_id(event):
    return event['job ID'], event['task index']


def event_summary(event, invert=False):
    multiplier = -1 if invert else 1
    return {
        'time': event['time'],
        'cpu': multiplier * event['CPU request'],
        'memory': multiplier * event['memory request']
    }

# thread sync and control
done = threading.Event()
type_events_locks = defaultdict(threading.Lock)
type_events = defaultdict(deque)

test_locker = threading.Lock()


def aggregate_user_events(dataset_dir, save_dir):
    schema = Schema(dataset_dir)

    saving_thread = threading.Thread(target=save_user_agg_events,
                                     args=(save_dir,))
    saving_thread.start()

    files = sorted(listdir(path.join(dataset_dir, 'task_events')))
    print 'files: ', files
    for i, f in enumerate(files):
        print 'file %i of %i' % (i+1, len(files))
        task_events_df = pd.read_csv(path.join(dataset_dir, 'task_events', f),
                                     header=None, index_col=False,
                                     compression='gzip', names=schema.task_events)
        print task_events_df.shape

        for index, event in task_events_df.iterrows():
            if not np.isnan(event['missing info']):
                continue

            event_type = event['event type']
            user = event['user']
            test_locker.acquire()
            type_events_locks[user].acquire()
            if event_type == 0:  # new event
                type_events[user].append(event_summary(event))
            elif 2 <= event_type <= 6:
                type_events[user].append(event_summary(event,invert=True))
            type_events_locks[user].release()
            test_locker.release()

    print "done reading files, now finishing save..."

    done.set()
    saving_thread.join()


def save_user_agg_events(dir):
    user_index_generator = itertools.count()
    user_index = defaultdict(user_index_generator.next)

    def save():
        test_locker.acquire()
        for user in type_events.keys():
            type_events_locks[user].acquire()
            user_type_events = type_events[user]
            if len(user_type_events) == 0:
                type_events_locks[user].release()
                continue
            time = [e['time'] for e in user_type_events]
            cpu = [e['cpu'] for e in user_type_events]
            memory = [e['memory'] for e in user_type_events]
            type_events[user].clear()
            type_events_locks[user].release()

            with open(path.join(dir, '%s.csv' % user_index[user]), 'a') as f:
                wr = csv.writer(f)
                for t, c, m in zip(time, cpu, memory):
                    wr.writerow([t, c, m])
        test_locker.release()

    while not done.is_set():
        save()
        time.sleep(1)
    save()

    with open(path.join(dir, 'users.csv'), 'w') as users_index_file:
        wr = csv.writer(users_index_file)
        for user, index in user_index.iteritems():
            wr.writerow([index, user])
