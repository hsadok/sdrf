# -*- coding: utf-8 -*-
import threading
from os import path
import csv

from sdrf.allocators.arrival.wdrf import WDRF
from sdrf.allocators.arrival.sdrf import MMMDRF, Reserved3MDRF
from sdrf.helpers.file_name import FileName
from sdrf.tasks import tasks_generator, save_from_deque, tasks_file_header
from sdrf.tasks.system_utilization import SystemUtilization


def wdrf(tasks_file, saving_dir, resource_percentage, use_weights=False):
    system_utilization = SystemUtilization(tasks_file)
    saving_file = FileName('task_sim', 'wdrf', resource_percentage,
                           weighted=use_weights).name

    if use_weights:
        users_weights_dict = {}
        for user in system_utilization.users_cpu_mean.keys():
            users_weights_dict[user] = [
                system_utilization.users_cpu_mean[user] /
                system_utilization.cpu_mean,
                system_utilization.users_memory_mean[user] /
                system_utilization.memory_mean
            ]
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
    saving_file = FileName('task_sim', '3mdrf', resource_percentage, delta,
                           same_share=same_share, reserved=reserved).name

    if same_share:
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
