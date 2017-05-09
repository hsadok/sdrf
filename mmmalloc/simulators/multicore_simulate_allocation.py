# -*- coding: utf-8 -*-

import multiprocessing
import psutil
import time
from simulate_allocation import simulate_allocation
from helpers.allocation import Allocation
from helpers.file_name import FileName


def multicore_simulate_allocation(dataset_file, saving_dir,
                                  estimate_memory_usage, deltas,
                                  resource_percentages):

    resource_type = FileName(dataset_file).attributes['resource_type']
    print resource_type

    alloc = Allocation(saving_dir)
    completed = [(a['delta'], a['resource_percentage']) for a
                 in alloc._allocations[resource_type]]

    jobs = []
    for delta in deltas:
        for res_percentage in resource_percentages:
            if (delta, res_percentage) in completed:
                print 'ignoring: delta = %f, resource percentage = %f' % \
                      (delta, res_percentage)
                continue
            args = (dataset_file, saving_dir, delta, res_percentage)
            p = multiprocessing.Process(target=simulate_allocation, args=args)
            jobs.append(p)

    available_memory = psutil.virtual_memory().available
    number_concurrent_jobs = available_memory/estimate_memory_usage

    for i, job in enumerate(jobs):
        while number_concurrent_jobs <= 0:
            time.sleep(1)
            available_memory = psutil.virtual_memory().available
            number_concurrent_jobs = available_memory/estimate_memory_usage
        print 'job %i' % (i+1,)
        job.start()
        number_concurrent_jobs -= 1

    for job in jobs:
        job.join()
