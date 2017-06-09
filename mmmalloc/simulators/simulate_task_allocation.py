# -*- coding: utf-8 -*-
import threading
from os import path

from mmmalloc.allocators.arrival.wdrf import WDRF
from mmmalloc.allocators.arrival.mmm_drf import MMMDRF
from mmmalloc.helpers.file_name import FileName
from mmmalloc.tasks import tasks_generator, save_from_deque, tasks_file_header
from mmmalloc.tasks.system_utilization import SystemUtilization


# def wdrf(system_resources, resource_percentage, saving_dir, tasks_file,
# weights):
def wdrf(tasks_file, saving_dir, resource_percentage, weights=None):
    system_utilization = SystemUtilization(tasks_file)

    if weights is None:
        weights = [1] * system_utilization.num_users

    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]
    allocator = WDRF(system_resources, weights)

    saving_file = FileName('task_sim', 'wdrf', resource_percentage)
    saving_file = path.join(saving_dir, saving_file.name)

    simulate_task_allocation(allocator, tasks_file, saving_file)


# def mmm_drf(system_resources, users_resources, resource_percentage,
# saving_dir, tasks_file):
def mmm_drf(tasks_file, saving_dir, resource_percentage, delta,
            same_share=False):
    print 'resource percentage: ', resource_percentage
    system_utilization = SystemUtilization(tasks_file)
    system_resources = [system_utilization.cpu_mean * resource_percentage,
                        system_utilization.memory_mean * resource_percentage]

    users_resources_dict = {}
    saving_file = FileName('task_sim', '3mdrf', resource_percentage).name

    if same_share:
        dot_split = saving_file.split('.')
        saving_file ='.'.join(dot_split[0:-1]) + '-same_share.' + dot_split[-1]
        resource_share = resource_percentage / system_utilization.num_users
        user_cpu = system_utilization.cpu_mean * resource_share
        user_memory = system_utilization.memory_mean * resource_share
        for user in system_utilization.users_cpu_mean.keys():
            users_resources_dict[user] = [user_cpu, user_memory]
    else:
        for user in system_utilization.users_cpu_mean.keys():
            users_resources_dict[user] = [
                system_utilization.users_cpu_mean[user] * resource_percentage,
                system_utilization.users_memory_mean[user] *resource_percentage
            ]

    allocator = MMMDRF(system_resources, users_resources_dict, delta=delta)

    saving_file = path.join(saving_dir, saving_file)
    simulate_task_allocation(allocator, tasks_file, saving_file)


def simulate_task_allocation(allocator, tasks_file, saving_file):
    done = threading.Event()
    saving_thread = threading.Thread(target=save_from_deque, args=(
        allocator.finished_tasks, saving_file, tasks_file_header, done))
    saving_thread.start()
    allocator.simulate(tasks_generator(tasks_file))
    done.set()
    saving_thread.join()
