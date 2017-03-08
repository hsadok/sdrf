import click

from user_types import aggregate_user_events
from user_types import generate_user_needs
from user_types import sample_needs
from simulators import simulate_allocation


@click.group()
def cli():
    pass


@cli.command(help='Separate cpu & memory requests for each user.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def aggregate_user_events(*args, **kwargs):
    aggregate_user_events.aggregate_user_events(*args, **kwargs)


@cli.command(help='Aggregate requests in the same timestamp.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
def generate_user_needs(*args, **kwargs):
    generate_user_needs.generate_all_user_needs(*args, **kwargs)


@cli.command(help='Sample needs following a scheduling period.')
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('scheduling_period', type=click.INT)
@click.argument('resource_type', type=click.Choice(['cpu', 'memory']))
@click.option('--num_users', default=0)
def sample_needs(*args, **kwargs):
    sample_needs.sample_needs(*args, **kwargs)


@cli.command(help='Simulate allocation.')
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('delta', type=click.FLOAT)
@click.argument('resource_percentage', type=click.FLOAT)
@click.argument('free_riders', default=0)
def simulate_allocation(*args, **kwargs):
    simulate_allocation.simulate_allocation(*args, **kwargs)


if __name__ == '__main__':
    cli()
