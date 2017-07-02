# -*- coding: utf-8 -*-
import threading
from os import path
import csv

from mmmalloc.allocators.arrival.wdrf import WDRF
from mmmalloc.allocators.arrival.mmm_drf import MMMDRF, Reserved3MDRF
from mmmalloc.helpers.file_name import FileName
from mmmalloc.tasks import tasks_generator, save_from_deque, tasks_file_header
from mmmalloc.tasks.system_utilization import SystemUtilization


def wdrf(tasks_file, saving_dir, resource_percentage, use_weights=False):
    system_utilization = SystemUtilization(tasks_file)
    saving_file = FileName('task_sim', 'wdrf', resource_percentage).name

    if use_weights:
        users_weights_dict = {}
        for user in system_utilization.users_cpu_mean.keys():
            users_weights_dict[user] = [
                system_utilization.users_cpu_mean[user] /
                system_utilization.cpu_mean,
                system_utilization.users_memory_mean[user] /
                system_utilization.memory_mean
            ]
        dot_split = saving_file.split('.')
        saving_file = '.'.join(dot_split[0:-1]) + '-weighted.' + dot_split[-1]
    else:
        users_weights_dict = None

    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]
    allocator = WDRF(system_resources, system_utilization.num_users,
                     users_weights_dict)

    saving_file = path.join(saving_dir, saving_file)
    simulate_task_allocation(allocator, tasks_file, saving_file)


def mmm_drf(tasks_file, saving_dir, resource_percentage, delta,
            same_share=False, reserved=False):
    print 'resource percentage: ', resource_percentage
    print 'delta: ', delta
    system_utilization = SystemUtilization(tasks_file)
    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]

    users_resources_dict = {}
    saving_file = FileName('task_sim', '3mdrf', resource_percentage,delta).name

    if same_share:
        dot_split = saving_file.split('.')
        saving_file ='.'.join(dot_split[0:-1]) + '-same_share.' + dot_split[-1]
        for user in system_utilization.users_cpu_mean.keys():
            users_resources_dict[user] = [0.0, 0.0]
    else:
        for user in system_utilization.users_cpu_mean.keys():
            users_resources_dict[user] = [
                system_utilization.users_cpu_mean[user] * resource_percentage,
                system_utilization.users_memory_mean[user] *resource_percentage
            ]

    with open(tasks_file, 'rb') as f:
        csv_reader = csv.reader(f)
        row = csv_reader.next()
        start_time = int(row[0])

    if reserved:
        dot_split = saving_file.split('.')
        saving_file = '.'.join(dot_split[0:-1]) + '-reserved.' + dot_split[-1]
        allocator = Reserved3MDRF(system_resources, users_resources_dict,
                                  delta, start_time)
    else:
        allocator = MMMDRF(system_resources, users_resources_dict, delta,
                           start_time)

    saving_file = path.join(saving_dir, saving_file)
    simulate_task_allocation(allocator, tasks_file, saving_file)

    allocator.print_stats('end - resource_percentage:%f' % resource_percentage)


def simulate_task_allocation(allocator, tasks_file, saving_file):
    done = threading.Event()
    saving_thread = threading.Thread(target=save_from_deque, args=(
        allocator.finished_tasks, saving_file, tasks_file_header, done))
    saving_thread.start()
    allocator.simulate(tasks_generator(tasks_file))
    done.set()
    saving_thread.join()
