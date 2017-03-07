# -*- coding: utf-8 -*-

import multiprocessing
import psutil
import time
import click
import json
import ConfigParser as configparser
from simulate_allocation import simulate_allocation
from helpers.allocation import Allocation
from helpers.file_name import FileName

def multicore_simulate_allocation(dataset_file, saving_dir,
                                  estimate_memory_usage, deltas,
                                  resource_percentages, free_riders):

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
            args = (dataset_file, saving_dir, delta, res_percentage,
                    free_riders)
            p = multiprocessing.Process(target=simulate_allocation, args=args)
            jobs.append(p)

    available_memory = psutil.virtual_memory().available
    number_concurrent_jobs = available_memory/estimate_memory_usage

    for i, job in enumerate(jobs):
        while number_concurrent_jobs <= 0:
            time.sleep(60)
            available_memory = psutil.virtual_memory().available
            number_concurrent_jobs = available_memory/estimate_memory_usage
        print 'job %i' % (i+1,)
        job.start()
        number_concurrent_jobs -= 1

    for job in jobs:
        job.join()


@click.command()
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('config_file', type=click.Path(exists=True, file_okay=True,
                                               dir_okay=False, readable=True))
def main(dataset_file, saving_dir, config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    estimate_memory_usage = config.getint("config", "estimate_memory_usage")
    deltas = json.loads(config.get("config", "deltas"))
    resource_percentages = json.loads(config.get("config", "resources"))
    free_riders = config.getint("config", "free_riders")

    multicore_simulate_allocation(dataset_file, saving_dir,
                                  estimate_memory_usage, deltas,
                                  resource_percentages, free_riders)


if __name__ == '__main__':
    main()
