# -*- coding: utf-8 -*-
from collections import deque

import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib; matplotlib.use('PDF')
import matplotlib.pyplot as plt

from mmmalloc.helpers.schema import SchemaIndex
from mmmalloc.tasks import tasks_file_header


def df_mean(df, column):
    period = df.index[-1] - df.index[0]
    x = df.index
    y = df[column].as_matrix()
    return np.sum(np.diff(x) * y[:-1]) / period


def utilization_over_time(tasks_file, saving_file):
    print 'reading...'
    tasks_df = pd.read_csv(tasks_file, header=None, index_col=False,
                           names=tasks_file_header)
    task_index = SchemaIndex(tasks_file_header)
    events = deque()
    print 'processing lines...'
    for task_line in tqdm(tasks_df.itertuples(), total=len(tasks_df)):
        start_time = task_line[task_index['start_time']]
        finish_time = task_line[task_index['finish_time']]
        cpu = task_line[task_index['cpu']]
        memory = task_line[task_index['memory']]
        events.append((start_time, cpu, memory))
        events.append((finish_time, -cpu, -memory))

    del tasks_df
    events = sorted(events)
    first_event = events.pop(0)
    aggregated_time = deque([first_event[0]])
    aggregated_cpu = deque([first_event[1]])
    aggregated_memory = deque([first_event[2]])
    for t, c, m in tqdm(events, total=len(events)):
        if t == aggregated_time[-1]:
            aggregated_cpu[-1] += c
            aggregated_memory[-1] += m
        else:
            aggregated_time.append(t)
            aggregated_cpu.append(c)
            aggregated_memory.append(m)

    cum_cpu = np.cumsum(aggregated_cpu)
    cum_memory = np.cumsum(aggregated_memory)

    del aggregated_cpu
    del aggregated_memory

    print 'max CPU utilization: ', np.max(cum_cpu)
    print 'max memory utilization: ', np.max(cum_memory)

    dt_time = pd.to_datetime(list(aggregated_time), unit='us')

    df = pd.DataFrame({'cpu': cum_cpu, 'memory': cum_memory}, index=dt_time)
    print 'mean CPU utilization: ', df_mean(df, 'cpu')
    print 'mean memory utilization: ', df_mean(df, 'memory')
    df = df.resample('1T').mean()
    df.fillna(method='pad', inplace=True)
    plt.figure(figsize=(8, 4))
    df.plot()
    plt.savefig(saving_file)
