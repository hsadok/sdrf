# -*- coding: utf-8 -*-

import click
from os import listdir, path
from progress.bar import Bar
import pandas as pd
import numpy as np

from helpers.file_name import FileName


def sample_needs(dataset_path, saving_dir, scheduling_period, resource_type,
                 num_users=0):
    files = sorted(listdir(dataset_path))
    if 'users.csv' in files:
        files.remove('users.csv')

    res_list = []
    for f in Bar('Loading files').iter(files):
        df = pd.read_csv(path.join(dataset_path, f), header=None,
                         index_col=None, names=['time', 'cpu'+f, 'memory'+f])
        df['time'] = pd.to_datetime(df['time'], unit='us')
        df.set_index('time', inplace=True)
        res = df[resource_type+f]
        res[res < 0] = 0
        res_list.append(res)

    for i, df in enumerate(res_list):
        res_list[i] = df.resample('%iS' % scheduling_period, label='right',
                                  closed='right').pad()
    res_df = pd.concat(res_list, axis=1, copy=False)
    del res_list
    res_df.fillna(method='pad', inplace=True)
    res_df.fillna(value=0, inplace=True)
    res_df = res_df.apply(lambda x: np.ceil(x*1e4).astype(np.int64), raw=True)
    file_name = FileName('user_needs', resource_type, scheduling_period,
                         num_users).name

    if num_users != 0:
        res_df = res_df.sample(num_users, axis=1, random_state=42)

    res_df.to_csv(path.join(saving_dir, file_name))


@click.command()
@click.argument('dataset_path', type=click.Path(exists=True, file_okay=False,
                                                readable=True))
@click.argument('saving_dir', type=click.Path(exists=True, file_okay=False,
                                              writable=True))
@click.argument('scheduling_period', type=click.INT)
@click.argument('resource_type', type=click.Choice(['cpu', 'memory']))
@click.option('--num_users', default=0)
def main(*args, **kwargs):
    sample_needs(*args, **kwargs)

if __name__ == '__main__':
    main()
