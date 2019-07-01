# -*- coding: utf-8 -*-
import click
import json
import sys
from itertools import product
import ConfigParser as configparser

from sdrf.helpers.file_name import FileName


@click.group()
def cli():
    pass


@cli.command(help='Parse Google cluster data filtering problematic tasks.')
@click.argument('dataset_dir', type=click.Path(exists=True, file_okay=False,
                                               readable=True))
@click.argument('saving_file', type=click.Path(file_okay=True, writable=True,
                                               dir_okay=False))
def parse_google_tasks(*args, **kwargs):
    from sdrf.tasks.filter_tasks import filter_tasks
    filter_tasks(*args, **kwargs)


@cli.command(help='Plot system utilization with filtered tasks.')
@click.argument('tasks_file', type=click.Path(exists=True, file_okay=True,
                                              dir_okay=False, readable=True),
                nargs=-1)
def system_utilization(tasks_file):
    from sdrf.tasks.system_utilization import SystemUtilization
    for f in tasks_file:
        if '.' in f:
            dot_split = f.split('.')
            saving_file = '.'.join(dot_split[0:-1]) + '.pdf'
        else:
            saving_file = f + '.pdf'
        SystemUtilization(f).plot(saving_file)


@cli.command(help='Simulate task allocation using a TASKS_FILE generated with '
                  'the filter_tasks subcommand. Result is saved to the same di'
                  'rectory or to SAVING_PATH.')
@click.argument('tasks_file', type=click.Path(exists=True, file_okay=True,
                                              dir_okay=False, readable=True))
@click.argument('saving_path', type=click.Path(file_okay=True, dir_okay=True,
                                               writable=True), required=False)
@click.option('--allocator', '-a', type=click.Choice(['wdrf', 'sdrf']),
              default='sdrf', help='Allocator to use (defaults to sdrf).')
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True),
              help='Configuration file to use.')
@click.option('--delta', '-d', type=click.FLOAT, multiple=True,
              help='Delta to be used by SDRF. When more than one value is prov'
                   'ided, a simulation is run for each.')
@click.option('--resource', '-r', type=click.FLOAT, multiple=True,
              help='Percentage of resources used by the user provided in the s'
                   'imulation, e.g., if a user in the dataset has an average u'
                   'sage of 2 resources per hour and this option is 1.1, we gi'
                   've this user 2.2 resources as their own. When more than on'
                   'e value is provided, a simulation is run for each.')
@click.option('--same_share', is_flag=True,
              help='This makes the resource option be used only for the amount'
                   ' of resources in the system instead of for each user. In t'
                   'his mode all users get the same share (0). This only makes'
                   ' sense for SDRF.')
@click.option('--reserved', is_flag=True,
              help='Enables the 2 stages queue for SDRF. First stage uses a D'
                   'RF queue and tries to enforce reserved resources for each'
                   ' user. The second stage is a regular DRF queue.')
@click.option('--weights', '-w', is_flag=True,
              help='This makes DRF act as wDRF using weights proportional to u'
                   'sers\' resources.')
def simulate_task_allocation(tasks_file, saving_path, allocator, config, delta,
                             resource, same_share, reserved, weights):

    if (not config) and (not resource):
        print('Must provide a config file or at least one resource percentage')
        sys.exit(1)
    if allocator == 'sdrf' and (not config) and (not delta):
        print('Must provide a config file or at least one delta')
        sys.exit(2)

    if config:
        conf_parser = configparser.ConfigParser()
        conf_parser.read(config)
        try:
            resource = json.loads(conf_parser.get('config', 'resources'))
            if allocator == 'sdrf':
                delta = json.loads(conf_parser.get('config', 'deltas'))
        except configparser.NoOptionError as e:
            print ('No option "%s" found in the config file.' % e.option)
            sys.exit(3)

    saving_path = saving_path or '.'

    if allocator == 'wdrf':
        from sdrf.simulators.simulate_task_allocation import wdrf as sim
        arg_iterator = product([tasks_file], [saving_path], resource,[weights])
    else:  # sdrf
        from sdrf.simulators.simulate_task_allocation import sdrf as sim
        arg_iterator = product([tasks_file], [saving_path], resource, delta,
                               [same_share], [reserved])
    for arg in arg_iterator:
        sim(*arg)


@cli.command(help='Summary of tasks execution from a tasks file.')
@click.argument('tasks_file', type=click.Path(exists=True, file_okay=True,
                                              dir_okay=False, readable=True),
                nargs=-1)
def jobs_summary(tasks_file):
    from sdrf.tasks.jobs_summary import jobs_summary as run_jobs_summary
    for f in tasks_file:
        file_att = FileName(f)
        allocator = file_att.attributes.pop('allocator')
        resource_percentage = file_att.attributes.pop('resource_percentage')
        delta = file_att.attributes.pop('delta')
        file_att.attributes['jobs'] = True
        saving_file = FileName('task_sim', allocator, resource_percentage,
                               delta, **file_att.attributes)
        saving_file = saving_file.name
        run_jobs_summary(f, saving_file)


if __name__ == '__main__':
    cli(prog_name='python -m sdrf')

