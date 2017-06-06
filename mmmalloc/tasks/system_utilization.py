# -*- coding: utf-8 -*-
from collections import deque, defaultdict
from hashlib import sha256
import pandas as pd
import numpy as np
import json
from os.path import join, dirname, abspath, exists
import matplotlib; matplotlib.use('PDF')
import matplotlib.pyplot as plt
from tqdm import tqdm

from mmmalloc.helpers.schema import SchemaIndex
from mmmalloc.tasks import tasks_file_header


def df_mean(df, column, period=None):
    if period is None:
        period = df.index[-1] - df.index[0]
    x = df.index
    y = df[column].as_matrix()
    return np.sum(np.diff(x) * y[:-1]) / period


def events_to_usage(events):
    events = sorted(events)
    first_event = events.pop(0)
    aggregated_time = deque([first_event[0]])
    aggregated_cpu = deque([first_event[1]])
    aggregated_memory = deque([first_event[2]])
    for t, c, m in events:
        if t == aggregated_time[-1]:
            aggregated_cpu[-1] += c
            aggregated_memory[-1] += m
        else:
            aggregated_time.append(t)
            aggregated_cpu.append(c)
            aggregated_memory.append(m)

    cum_cpu = np.cumsum(aggregated_cpu)
    cum_memory = np.cumsum(aggregated_memory)

    return aggregated_time, cum_cpu, cum_memory


class SystemUtilization(object):
    def __init__(self, tasks_file, cache_file=None):
        self.tasks_file = tasks_file
        self.tasks_file_sha = sha256(open(tasks_file, 'rb').read()).hexdigest()

        if cache_file is None:
            cache_file = join(dirname(abspath(tasks_file)), 'cred_cache.json')

        self.cache_file = cache_file

        self._save_properties = ['cpu_mean', 'memory_mean', 'cpu_peak',
                                 'memory_peak', 'users_cpu_mean',
                                 'users_memory_mean', 'users_cpu_peak',
                                 'users_memory_peak', 'number_of_users']

        for att in self._save_properties:
            setattr(self, '_' + att, None)

        self._data_df = None
        self.load_from_cache()

    @property
    def num_users(self):
        return len(self.users_cpu_peak)

    def __getattr__(self, name):
        if name in self._save_properties:
            if getattr(self, '_' + name) is None:
                self.calculate()
            return getattr(self, '_' + name)
        raise AttributeError(name)

    def plot(self, saving_file):
        if self._data_df is None:
            self.calculate()
        df = self._data_df.resample('1T').mean()
        df.fillna(method='pad', inplace=True)
        plt.figure(figsize=(8, 4))
        df.plot()
        plt.savefig(saving_file)

    def calculate(self):
        tasks_df = pd.read_csv(self.tasks_file, header=None, index_col=False,
                               names=tasks_file_header)
        task_index = SchemaIndex(tasks_file_header)
        events = deque()
        events_by_user = defaultdict(deque)
        for task_line in tqdm(tasks_df.itertuples(), total=len(tasks_df)):
            start_time = task_line[task_index['start_time']]
            finish_time = task_line[task_index['finish_time']]
            cpu = task_line[task_index['cpu']]
            memory = task_line[task_index['memory']]
            user = task_line[task_index['user_id']]
            events.append((start_time, cpu, memory))
            events.append((finish_time, -cpu, -memory))
            events_by_user[user].append((start_time, cpu, memory))
            events_by_user[user].append((finish_time, -cpu, -memory))

        self._number_of_users = len(events_by_user)
        del tasks_df

        aggregated_time, cum_cpu, cum_memory = events_to_usage(events)

        self._cpu_peak = np.max(cum_cpu)
        self._memory_peak = np.max(cum_memory)

        dt_time = pd.to_datetime(list(aggregated_time), unit='us')
        self._data_df = pd.DataFrame({'cpu': cum_cpu, 'memory': cum_memory},
                                     index=dt_time)
        period = self._data_df.index[-1] - self._data_df.index[0]
        self._cpu_mean = df_mean(self._data_df, 'cpu')
        self._memory_mean = df_mean(self._data_df, 'memory')

        self._users_cpu_mean = {}
        self._users_memory_mean = {}
        self._users_cpu_peak = {}
        self._users_memory_peak = {}

        print 'now users'
        for user, events in tqdm(events_by_user.iteritems(),
                                 total=len(events_by_user)):
            aggregated_time, cum_cpu, cum_memory = events_to_usage(events)
            self._users_cpu_peak[user] = np.max(cum_cpu)
            self._users_memory_peak[user] = np.max(cum_memory)

            dt_time = pd.to_datetime(list(aggregated_time), unit='us')

            user_data_df = pd.DataFrame({'cpu': cum_cpu,
                                          'memory': cum_memory}, index=dt_time)
            self._users_cpu_mean[user] = df_mean(user_data_df, 'cpu', period)
            self._users_memory_mean[user] = df_mean(user_data_df, 'memory',
                                                    period)

        self.save_to_cache()

    def load_from_cache(self):
        if not exists(self.cache_file):
            return
        with open(self.cache_file, 'r') as f:
            cache_data = json.load(f)
            if self.tasks_file_sha in cache_data:
                tasks_data = cache_data[self.tasks_file_sha]
                for property in self._save_properties:
                    setattr(self, '_' + property, tasks_data.get(property))

    def save_to_cache(self):
        cache_data = {}
        if exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
        data = {k: getattr(self, '_' + k) for k in self._save_properties}
        cache_data[self.tasks_file_sha] = data
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)
