import csv
from collections import defaultdict
import itertools
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib2tikz import save as tikz_save

from mmmalloc.tasks import tasks_generator, jobs_file_header

# matplotlib.rcParams['lines.linewidth'] = .2
# plt.style.use('seaborn-deep')

### overall system performance ###

# plot bar plot like the DRF paper showing completion time reduction (compared
# to DRF) for jobs with different number of tasks

# plot a CDF of completion time reduction: for every possible job calculate the
# completion time reduction. Some jobs will perform better, some not.

# we can do the same thing for completion time from submit to finish (this is
# what really matters after all) and only for the waiting time


# scatter plot of tasks waiting time all tasks for all users

### individual performance ###

# plot waiting time (start_time - submit_time) for users of different
# credibilities (can compare it against plain DRF)


def plot_bar_graph(min_value=5, max_value=25, nb_samples=5):
    """Plot two bar graphs side by side, with letters as x-tick labels.
    """
    prng = np.random.RandomState(96917002)
    fig, ax = plt.subplots()

    x = np.arange(nb_samples)
    ya, yb = prng.randint(min_value, max_value, size=(2, nb_samples))
    width = 0.25
    ax.bar(x, ya, width)
    ax.bar(x + width, yb, width, color='C2')
    ax.set_xticks(x + width)
    ax.set_xticklabels([1, 2, 3, 4, 5])
    ax.set_axisbelow(True)
    ax.yaxis.grid(color='0.3', linestyle=':', linewidth=0.5)
    return ax


def tasks_scatter(name_file_list, ax=None):
    if ax is None:
        ax = plt.subplots()[1]

    user_shift = 0.0
    for name, task_file in name_file_list:
        wait_times = []
        users = []
        for task in tasks_generator(task_file):
            wait_times.append(task.start_time - task.submit_time)
            users.append(task.user + user_shift)
        ax.scatter(wait_times, users, marker='x', s=1, label=name)
        user_shift += 0.1
    ax.legend()


def jobs_scatter(name_file_list, ax=None):
    if ax is None:
        ax = plt.subplots()[1]

    user_shift = 0.0
    user_counter = itertools.count()
    user_id_mapper = defaultdict(user_counter.next)
    for name, job_file in name_file_list:
        wait_times = []
        users = []
        with open(job_file) as f:
            rd = csv.DictReader(f, fieldnames=jobs_file_header)
            for row in rd:
                wait_times.append(float(row['finish_time']) - float(row['submit_time']))
                users.append(user_id_mapper[row['user_id']] + user_shift)
        ax.scatter(wait_times, users, marker='x', s=1, label=name)
        user_shift += 0.1
    ax.legend()


def tasks_wait_cdf(name_file_list, ax=None):
    if ax is None:
        ax = plt.subplots()[1]
    for name, task_file in name_file_list:
        wait_times = []
        for task in tasks_generator(task_file):
            wait_times.append(task.start_time - task.submit_time)
        sorted = np.sort(wait_times)
        yvals = np.arange(1, len(sorted) + 1) / float(len(sorted))
        # sorted = sorted[::10]
        # yvals = yvals[::10]
        ax.plot(sorted, yvals, label=name)

    # ax.set_xscale("log")
    # ax.set_yscale("log")
    ax.set_xlabel("Task Scheduling Wait")
    ax.set_ylabel("Empirical CDF")
    ax.legend()


def jobs_completion_cdf(name_file_list, ax=None):
    if ax is None:
        ax = plt.subplots()[1]
    for name, job_file in name_file_list:
        wait_times = []
        with open(job_file) as f:
            rd = csv.DictReader(f, fieldnames=jobs_file_header)
            for row in rd:
                wait_times.append(float(row['finish_time']) - float(row['submit_time']))
        sorted = np.sort(wait_times)
        yvals = np.arange(1, len(sorted) + 1) / float(len(sorted))
        # sorted = sorted[::10]
        # yvals = yvals[::10]
        ax.plot(sorted, yvals, label=name)

    # ax.set_xscale("log")
    # ax.set_yscale("log")
    ax.set_xlabel("Jobs Completion Time")
    ax.set_ylabel("Empirical CDF")
    ax.legend()


def tasks_visualization(name_file, ax=None):
    if ax is None:
        ax = plt.subplots()[1]
    name, task_file = name_file
    submit_times = []
    waiting_period = []
    start_times = []
    running_period = []
    for task in tasks_generator(task_file):
        submit_times.append(task.submit_time)
        waiting_period.append(task.start_time - task.submit_time)
        start_times.append(task.start_time)
        running_period.append(task.finish_time - task.start_time)
    submit_times, start_times, waiting_period, running_period = zip(*sorted(zip(submit_times, start_times, waiting_period, running_period)))
    ax.barh(range(len(submit_times)), waiting_period, 1, left=submit_times)
    ax.barh(range(len(submit_times)), waiting_period, 1, left=start_times)

    print 'waiting: ', sum(waiting_period)
    print 'running: ', sum(running_period)

    ax.set_xlabel("Time $\mu$s")
    ax.set_ylabel("Job")


def jobs_visualization(name_file, ax=None):
    if ax is None:
        ax = plt.subplots()[1]
    name, job_file = name_file
    submit_times = []
    waiting_period = []
    start_times = []
    running_period = []
    with open(job_file) as f:
        rd = csv.DictReader(f, fieldnames=jobs_file_header)
        for row in rd:
            submit_times.append(float(row['submit_time']))
            waiting_period.append(float(row['start_time']) - float(row['submit_time']))
            start_times.append(float(row['start_time']))
            running_period.append(float(row['finish_time']) - float(row['start_time']))
    submit_times, start_times, waiting_period, running_period = zip(*sorted(zip(submit_times, start_times, waiting_period, running_period)))
    ax.barh(range(len(submit_times)), waiting_period, 1, left=submit_times)
    ax.barh(range(len(submit_times)), waiting_period, 1, left=start_times)

    print 'waiting: ', sum(waiting_period)
    print 'running: ', sum(running_period)

    ax.set_xlabel("Time $\mu$s")
    ax.set_ylabel("Job")

tasks2 = [
    ('DRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-2.0-0.csv'),
    ('WDRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-2.0-0-weighted.csv'),
    ('3M ($\\alpha=10^{0}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.0-same_share.csv'),
    ('3M ($\\alpha=10^{-1}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.9-same_share.csv'),
    ('3M ($\\alpha=10^{-2}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.99-same_share.csv'),
    ('3M ($\\alpha=10^{-3}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.999-same_share.csv'),
    ('3M ($\\alpha=10^{-4}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.9999-same_share.csv'),
    ('3M ($\\alpha=10^{-5}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.99999-same_share.csv')
]

tasks4 = [
    ('DRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0.csv'),
    ('WDRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0-weighted.csv'),
    ('3M ($\\alpha=10^{0}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.0.csv'),
    ('3M ($\\alpha=10^{-1}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9.csv'),
    ('3M ($\\alpha=10^{-2}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99.csv'),
    ('3M ($\\alpha=10^{-3}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.999.csv'),
    ('3M ($\\alpha=10^{-4}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9999.csv'),
    ('3M ($\\alpha=10^{-5}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99999.csv')
]

tasks4_same_share = [
    ('DRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0.csv'),
    ('WDRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0-weighted.csv'),
    ('3M ($\\alpha=10^{0}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.0-same_share.csv'),
    ('3M ($\\alpha=10^{-1}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9-same_share.csv'),
    ('3M ($\\alpha=10^{-2}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99-same_share.csv'),
    ('3M ($\\alpha=10^{-3}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.999-same_share.csv'),
    ('3M ($\\alpha=10^{-4}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9999-same_share.csv'),
    ('3M ($\\alpha=10^{-5}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99999-same_share.csv')
]

jobs2 = [
    ('DRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-2.0-0-jobs.csv'),
    ('WDRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-2.0-0-weighted-jobs.csv'),
    ('3M ($\\alpha=10^{0}$)' , '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.0-jobs.csv'),
    ('3M ($\\alpha=10^{-1}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.9-jobs.csv'),
    ('3M ($\\alpha=10^{-2}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.99-jobs.csv'),
    ('3M ($\\alpha=10^{-3}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.999-jobs.csv'),
    ('3M ($\\alpha=10^{-4}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.9999-jobs.csv'),
    ('3M ($\\alpha=10^{-5}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-2.0-0.99999-jobs.csv'),
]

jobs4 = [
    ('DRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0-jobs.csv'),
    ('WDRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0-weighted-jobs.csv'),
    ('3M ($\\alpha=10^{0}$)' , '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.0-jobs.csv'),
    ('3M ($\\alpha=10^{-1}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9-jobs.csv'),
    ('3M ($\\alpha=10^{-2}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99-jobs.csv'),
    ('3M ($\\alpha=10^{-3}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.999-jobs.csv'),
    ('3M ($\\alpha=10^{-4}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9999-jobs.csv'),
    ('3M ($\\alpha=10^{-5}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99999-jobs.csv'),
]

jobs4_same_share = [
    ('DRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0-jobs.csv'),
    ('WDRF', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-wdrf-4.0-0-weighted-jobs.csv'),
    ('3M ($\\alpha=10^{0}$)' , '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.0-same_share-jobs.csv'),
    ('3M ($\\alpha=10^{-1}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9-same_share-jobs.csv'),
    ('3M ($\\alpha=10^{-2}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99-same_share-jobs.csv'),
    ('3M ($\\alpha=10^{-3}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.999-same_share-jobs.csv'),
    ('3M ($\\alpha=10^{-4}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.9999-same_share-jobs.csv'),
    ('3M ($\\alpha=10^{-5}$)', '/Users/hugo/Dropbox/Estudos/UFRJ/GTA/mmm/test_data/task_sim-3mdrf-4.0-0.99999-same_share-jobs.csv'),
]

def main():
    # read 2 tasks file (i.e. wDRF and 3M-DRF)
    # plot bar plot for completion time reduction for different job sizes
    # improvement in executing time for some types of job
    # plt.bar()

    # plot_bar_graph()

    tasks_wait_cdf(tasks4_same_share)
    plt.savefig('tasks4.0_same_share_cdf.pdf')

    # jobs_scatter(jobs_simulations[2:])
    # plt.savefig('jobs_completion_scatter.pdf')
    #
    jobs_completion_cdf(jobs4_same_share)
    plt.savefig('jobs4.0_same_share_completion_cdf.pdf')

    # jobs_visualization(jobs_simulations[0])
    # plt.savefig('jobs_drf.pdf')
    # jobs_visualization(jobs_simulations[1])
    # plt.savefig('jobs_wdrf.pdf')
    # jobs_visualization(jobs_simulations[5])
    # plt.savefig('jobs_3mdrf_0.999.pdf')

    # tasks_visualization(simulations2[0])
    # plt.savefig('tasks_drf.pdf')
    # tasks_visualization(simulations2[1])
    # plt.savefig('tasks_wdrf.pdf')
    # tasks_visualization(simulations2[5])
    # plt.savefig('tasks_3mdrf_0.999.pdf')


    # tasks_scatter(simulations)
    # plt.savefig("plot_with_drf.pdf")
    #
    # tasks_scatter(simulations[2:])
    # plt.savefig("plot_no_drf.pdf")
    # tikz_save(
    #     'wait_cdf.tex',
    #     figureheight='\linewidth',
    #     figurewidth='200'
    # )


if __name__ == '__main__':
    main()
