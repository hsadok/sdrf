# -*- coding: utf-8 -*-
# This function aggregates all resource requests so that we have, at a given
# timestamp, the amount of resources needed by the user

import math
from os import listdir, path
import numpy as np
import pandas as pd
import csv


def generate_user_needs(file_name, saving_name=None):
    user_types_df = pd.read_csv(file_name, header=None, index_col=False,
                                names=['time', 'cpu', 'memory'])
    aggregated_time = [user_types_df.time[0]]
    aggregated_cpu = [user_types_df.cpu[0]]
    aggregated_memory = [user_types_df.memory[0]]
    for t, c, m in zip(user_types_df.time.tolist()[1:],
                       user_types_df.cpu.tolist()[1:],
                       user_types_df.memory.tolist()[1:]):
        if np.any(map(math.isnan, [t, c, m])):
            continue
        if t == aggregated_time[-1]:
            aggregated_cpu[-1] += c
            aggregated_memory[-1] += m
        else:
            aggregated_time.append(t)
            aggregated_cpu.append(c)
            aggregated_memory.append(m)

    cumulative_cpu = np.cumsum(aggregated_cpu)
    cumulative_memory = np.cumsum(aggregated_memory)
    if saving_name is None:
        saving_name = ''.join(file_name.split('.')[0:-1]) + '_timestamp.csv'
    with open(saving_name, 'w') as f:
        wr = csv.writer(f)
        for t, c, m in zip(aggregated_time, cumulative_cpu, cumulative_memory):
            wr.writerow([t, c, m])


def generate_all_user_needs(dataset_path, saving_dir):
    files = sorted(listdir(dataset_path))
    if 'users.csv' in files:
        files.remove('users.csv')
    for f in files:
        saving_name = path.join(saving_dir, f)
        print saving_name
        generate_user_needs(path.join(dataset_path, f), saving_name)
