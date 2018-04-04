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


@cli.command(help='Separate cpu & memory requests for each user.')
@click.argument('dataset_dir', type=click.Path(exists=True, file_okay=False,
                                               readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def aggregate_user_events(*args, **kwargs):
    from sdrf.user_types.aggregate_user_events import aggregate_user_events
    aggregate_user_events(*args, **kwargs)


@cli.command(help='Filter problematic tasks.')
@click.argument('dataset_dir', type=click.Path(exists=True, file_okay=False,
                                               readable=True))
@click.argument('saving_file', type=click.Path(file_okay=True, writable=True,
                                               dir_okay=False))
def filter_tasks(*args, **kwargs):
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


@cli.command(help='Aggregate requests in the same timestamp.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def generate_user_needs(*args, **kwargs):
    from sdrf.user_types.generate_user_needs import generate_all_user_needs
    generate_all_user_needs(*args, **kwargs)


@cli.command(help='Sample needs following a scheduling period.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('scheduling_period', type=click.INT)
@click.argument('resource_type', type=click.Choice(['cpu', 'memory']))
@click.option('--num_users', default=0)
def sample_needs(*args, **kwargs):
    from sdrf.user_types.sample_needs import sample_needs
    sample_needs(*args, **kwargs)


@cli.command(help='Simulate allocation.')
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('delta', type=click.FLOAT)
@click.argument('resource_percentage', type=click.FLOAT)
def simulate_allocation(*args, **kwargs):
    from sdrf.simulators.simulate_allocation import simulate_allocation
    simulate_allocation(*args, **kwargs)


@cli.command(help='Simulate task allocation using a TASKS_FILE generated with '
                  'the filter_tasks subcommand. Result is saved to the same di'
                  'rectory or to SAVING_PATH.')
@click.argument('tasks_file', type=click.Path(exists=True, file_okay=True,
                                              dir_okay=False, readable=True))
@click.argument('saving_path', type=click.Path(file_okay=True, dir_okay=True,
                                               writable=True), required=False)
@click.option('--allocator', '-a', type=click.Choice(['wdrf', '3mdrf']),
              default='3mdrf', help='Allocator to use (defaults to 3mdrf).')
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True),
              help='Configuration file to use.')
@click.option('--delta', '-d', type=click.FLOAT, multiple=True,
              help='Delta to be used by 3M-DRF. When more than one value is pr'
                   'ovided, a simulation is run for each.')
@click.option('--resource', '-r', type=click.FLOAT, multiple=True,
              help='Percentage of resources used by the user provided in the s'
                   'imulation, i.e. if a user in the dataset has an average us'
                   'age of 2 resources per hour and this option is 1.1, we giv'
                   'e this user 2.2 resources as their own. When more than one'
                   ' value is provided, a simulation is run for each.')
@click.option('--same_share', is_flag=True,
              help='This makes the resource option be used only for the amount'
                   ' of resources in the system instead of for each user. In t'
                   'his mode all users get the same share (0). This only make'
                   's sense for 3MDRF.')
@click.option('--reserved', is_flag=True,
              help='Enables the 2 stages queue for 3MDRF. First stage uses a D'
                   'RF queue and tries to enforce reserved resources for each'
                   ' user. The second stage is a regular 3M queue.')
@click.option('--weights', '-w', is_flag=True,
              help='This makes DRF act as wDRF using weights proportional to u'
                   'sers resources.')
def simulate_task_allocation(tasks_file, saving_path, allocator, config, delta,
                             resource, same_share, reserved, weights):
    if (not config) and (not resource):
        print('Must provide a config file or at least one resource percentage')
        sys.exit(1)
    if allocator == '3mdrf' and (not config) and (not delta):
        print('Must provide a config file or at least one delta')
        sys.exit(2)

    if config:
        conf_parser = configparser.ConfigParser()
        conf_parser.read(config)
        try:
            resource = json.loads(conf_parser.get('config', 'resources'))
            if allocator == '3mdrf':
                delta = json.loads(conf_parser.get('config', 'deltas'))
        except configparser.NoOptionError as e:
            print ('No option "%s" found in the config file.' % e.option)
            sys.exit(3)

    saving_path = saving_path or '.'

    if allocator == 'wdrf':
        from sdrf.simulators.simulate_task_allocation import wdrf as sim
        arg_iterator = product([tasks_file], [saving_path], resource,[weights])
    else:  # 3m-drf
        from sdrf.simulators.simulate_task_allocation import mmm_drf as sim
        arg_iterator = product([tasks_file], [saving_path], resource, delta,
                               [same_share], [reserved])
    for arg in arg_iterator:
        sim(*arg)


@cli.command(help='Get the summary of tasks execution from a tasks file.')
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


@cli.command(help='Calculate users credibilities over time.')
@click.argument('tasks_file',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                readable=True),
                nargs=-1)
@click.argument('original_dataset',
                type=click.Path(exists=True, file_okay=True,
                                dir_okay=False, readable=True))
def credibility_from_tasks(tasks_file, original_dataset):
    from sdrf.tasks.credibility import credibility_summary
    for f in tasks_file:
        if '.' in f:
            dot_split = f.split('.')
            saving_file = '.'.join(dot_split[0:-1]) + '-credibility.'\
                          + dot_split[-1]
        else:
            saving_file = f + '-credibility'

        credibility_summary(f, original_dataset, saving_file)


@cli.command(help='Simulate allocation using multiple cores.')
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('config_file', type=click.Path(exists=True, file_okay=True,
                                               dir_okay=False, readable=True))
def multicore_simulate_allocation(dataset_file, saving_dir, config_file):
    from sdrf.simulators.multicore_simulate_allocation import \
        multicore_simulate_allocation
    config = configparser.ConfigParser()
    config.read(config_file)
    estimate_memory_usage = config.getint('config', 'estimate_memory_usage')
    deltas = json.loads(config.get('config', 'deltas'))
    resource_percentages = json.loads(config.get('config', 'resources'))

    multicore_simulate_allocation(dataset_file, saving_dir,
                                  estimate_memory_usage, deltas,
                                  resource_percentages)


@cli.command(help='Run experiments.')
@click.argument('data_path',
                type=click.Path(exists=True, file_okay=False, readable=True))
def experiments(data_path):
    import sdrf.analysis.experiments2 as exp
    exp.request_fulfilment(data_path)
    exp.resource_vs_utility(data_path)
    exp.allocation_smoothness(data_path)
    exp.resource_utilization_bar_plot(data_path)
    exp.resources_received_vs_given(data_path)


if __name__ == '__main__':
    cli()
