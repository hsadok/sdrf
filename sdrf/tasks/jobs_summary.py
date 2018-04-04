import threading
from collections import deque, defaultdict

import sys

from sdrf.tasks import tasks_generator, jobs_file_header, save_from_deque


class RunningJob(object):
    def __init__(self):
        self.num_tasks = 0
        self.submit_time = sys.maxint
        self.start_time = sys.maxint
        self.finish_time = 0
        self.cpu_sum = 0.0
        self.memory_sum = 0.0

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def duration(self):
        return self.finish_time - self.start_time

    @property
    def cpu_mean(self):
        return self.cpu_sum / self.num_tasks

    @property
    def memory_mean(self):
        return self.memory_sum / self.num_tasks

    def add_task(self, task):
        self.num_tasks += 1
        self.cpu_sum += task.cpu
        self.memory_sum += task.memory
        self.submit_time = min(self.submit_time, task.submit_time)
        self.start_time = min(self.start_time, task.start_time)
        self.finish_time = max(self.finish_time, task.finish_time)


def jobs_summary(tasks_file, saving_file):
    jobs = deque()
    running_jobs = defaultdict(RunningJob)

    for task in tasks_generator(tasks_file):
        job_id = task.task_id.split('-')[0]
        running_jobs[(job_id, task.user_id)].add_task(task)

    done = threading.Event()
    saving_thread = threading.Thread(target=save_from_deque, args=(
        jobs, saving_file, jobs_file_header, done))
    saving_thread.start()

    for (job_id, user_id), job in running_jobs.iteritems():
        job.job_id = job_id
        job.user_id = user_id
        jobs.append(job)

    done.set()
    saving_thread.join()
