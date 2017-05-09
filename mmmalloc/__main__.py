import click
import json
import sys
import ConfigParser as configparser


@click.group()
def cli():
    pass


@cli.command(help='Separate cpu & memory requests for each user.')
@click.argument('dataset_dir', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def aggregate_user_events(*args, **kwargs):
    from user_types.aggregate_user_events import aggregate_user_events
    aggregate_user_events(*args, **kwargs)


@cli.command(help='Filter problematic tasks.')
@click.argument('dataset_dir', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_file', type=click.Path(file_okay=True, writable=True,
                                               dir_okay=False))
def filter_tasks(*args, **kwargs):
    from tasks.filter_tasks import filter_tasks
    filter_tasks(*args, **kwargs)


@cli.command(help='System utilization with filtered tasks.')
@click.argument('tasks_file', type=click.Path(exists=True, file_okay=True,
                                              dir_okay=False, readable=True))
@click.argument('saving_file', type=click.Path(file_okay=True, writable=True,
                                               dir_okay=False))
def system_utilization(*args, **kwargs):
    from tasks.system_utilization import utilization_over_time
    utilization_over_time(*args, **kwargs)


@cli.command(help='Aggregate requests in the same timestamp.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def generate_user_needs(*args, **kwargs):
    from user_types.generate_user_needs import generate_all_user_needs
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
    from user_types.sample_needs import sample_needs
    sample_needs(*args, **kwargs)


@cli.command(help='Simulate allocation.')
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('delta', type=click.FLOAT)
@click.argument('resource_percentage', type=click.FLOAT)
def simulate_allocation(*args, **kwargs):
    from simulators.simulate_allocation import simulate_allocation
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
def simulate_task_allocation(tasks_file, saving_path, allocator, config, delta,
                             resource):
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
        from simulators.simulate_task_allocation import wdrf
        wdrf(tasks_file, saving_path, resource)
    elif allocator == '3mdrf':
        from simulators.simulate_task_allocation import mmm_drf
        mmm_drf(tasks_file, saving_path, resource, delta)


@cli.command(help='Simulate allocation using multiple cores.')
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('config_file', type=click.Path(exists=True, file_okay=True,
                                               dir_okay=False, readable=True))
def multicore_simulate_allocation(dataset_file, saving_dir, config_file):
    from simulators.multicore_simulate_allocation import \
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
    import analysis.experiments2 as exp
    exp.request_fulfilment(data_path)
    exp.resource_vs_utility(data_path)
    exp.allocation_smoothness(data_path)
    exp.resource_utilization_bar_plot(data_path)
    exp.resources_received_vs_given(data_path)


if __name__ == '__main__':
    cli()
