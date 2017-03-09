import click
import json
import ConfigParser as configparser

@click.group()
def cli():
    pass


@cli.command(help='Separate cpu & memory requests for each user.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def aggregate_user_events(*args, **kwargs):
    from user_types.aggregate_user_events import aggregate_user_events
    aggregate_user_events(*args, **kwargs)


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
    estimate_memory_usage = config.getint("config", "estimate_memory_usage")
    deltas = json.loads(config.get("config", "deltas"))
    resource_percentages = json.loads(config.get("config", "resources"))

    multicore_simulate_allocation(dataset_file, saving_dir,
                                  estimate_memory_usage, deltas,
                                  resource_percentages)


@cli.command(help='Run experiments.')
@click.argument('data_path',
                type=click.Path(exists=True, file_okay=False, readable=True))
def experiments(data_path):
    import allocation_analysis.experiments2 as exp
    exp.request_fulfilment(data_path)
    exp.resource_vs_utility(data_path)
    exp.allocation_smoothness(data_path)
    exp.resource_utilization_bar_plot(data_path)
    exp.resources_received_vs_given(data_path)


if __name__ == '__main__':
    cli()
