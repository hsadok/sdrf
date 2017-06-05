from itertools import product
import ConfigParser as configparser
import sys
import json
from jug import Task
from mmmalloc.simulators.simulate_task_allocation import mmm_drf


def simulate_task_allocation(tasks_file, saving_path, config):
    conf_parser = configparser.ConfigParser()
    conf_parser.read(config)
    try:
        resource = json.loads(conf_parser.get('config', 'resources'))
        delta = json.loads(conf_parser.get('config', 'deltas'))
    except configparser.NoOptionError as e:
        print ('No option "%s" found in the config file.' % e.option)
        sys.exit(3)

    arg_iterator = product([tasks_file], [saving_path], resource, delta)

    for arg in arg_iterator:
        Task(mmm_drf, *arg)


tasks_file = sys.argv[1]
saving_path = sys.argv[2]
config_file = sys.argv[3]

simulate_task_allocation(tasks_file, saving_path, config_file)
