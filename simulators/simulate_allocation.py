# -*- coding: utf-8 -*-

from os import path
import numpy as np
import pandas as pd
from progress.bar import Bar
from progress.spinner import Spinner
import click

from allocators.hyperplane_allocation import allocate
from helpers.file_name import FileName


class Allocator(object):
    def __init__(self, number_users, delta, users_resources, num_periods=None):
        self._reputation = None
        self.number_users = number_users
        self.delta = delta
        self.users_resources = users_resources

        if num_periods is not None:
            if num_periods == 0:
                self.progress = Spinner('Processing ')
            else:
                self.progress = Bar('Processing %(eta_td)s', max=num_periods)
        else:
            def dummy_progress():
                while True:
                    yield
            self.progress = dummy_progress()

    @property
    def reputation(self):
        if self._reputation is None:
            return np.zeros(self.number_users)
        return self._reputation

    def update_reputation(self, new_output):
        # the first call to update will only populate the reputation, this is
        # useful as the df.apply calls the function twice for the first row
        if self._reputation is None:
            self._reputation = np.zeros(self.number_users)
        else:
            self._reputation *= self.delta
            self._reputation += (1-self.delta) * new_output
            self.progress.next()
        return self._reputation

    def allocate_series(self, requested_resources):
        desire = requested_resources - self.users_resources
        new_output = np.array(allocate(desire.as_matrix(), self.reputation))
        self.update_reputation(new_output)
        return new_output


def simulate_allocation(dataset_file, saving_dir, delta, resource_percentage,
                        free_riders):
    att = FileName(dataset_file).attributes
    resource_type = att['resource_type']
    scheduling_period = att['scheduling_period']
    res_df = pd.read_csv(dataset_file, index_col='time')

    res_means = res_df.mean()
    user_resources = resource_percentage * res_means
    user_resources = user_resources.apply(lambda x:np.ceil(x).astype(np.int64))

    for i in xrange(free_riders):
        user_name = 'fr%i' % i
        res_df[user_name] = int(1e9)
        user_resources[user_name] = 0

    number_of_users = res_df.shape[1]
    num_periods = len(res_df)

    allocator = Allocator(number_of_users, delta, user_resources, num_periods)
    print 'simulation start'
    allocation = res_df.apply(allocator.allocate_series, axis=1, raw=True)
    allocator.progress.finish()

    print '\n'

    alloc_file_name = FileName('alloc', resource_type, scheduling_period,
                               delta, resource_percentage, free_riders)
    credibility_file_name = FileName('credibility', resource_type,
                                     scheduling_period, delta,
                                     resource_percentage, free_riders)

    allocation.to_csv(path.join(saving_dir, alloc_file_name.name))
    np.savetxt(path.join(saving_dir, credibility_file_name.name),
               allocator.reputation, delimiter=',')

    with open(path.join(saving_dir, 'INDEX.txt'), 'a') as f:
        f.write('%s: {scheduling_period: %i, delta: %f, resource_percentage: '
                '%f, resource_type: %s}\n' %
                (alloc_file_name.name, scheduling_period, delta,
                 resource_percentage, resource_type))


@click.command()
@click.argument('dataset_file', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('delta', type=click.FLOAT)
@click.argument('resource_percentage', type=click.FLOAT)
@click.argument('free_riders', default=0)
def main(*args, **kwargs):
    simulate_allocation(*args, **kwargs)

if __name__ == '__main__':
    main()
