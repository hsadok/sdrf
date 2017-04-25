# -*- coding: utf-8 -*-
from os import listdir, path
import pandas as pd
from progress.bar import Bar

from helpers.schema import Schema


def task_events(dataset_dir, progress=False):
    schema = Schema(dataset_dir)
    task_events_schema = schema.task_events
    files = sorted(listdir(path.join(dataset_dir, 'task_events')))
    if progress:
        files = Bar('Processing %(eta_td)s', max=len(files)).iter(files)
    for i, f in enumerate(files):
        task_events_df = pd.read_csv(path.join(dataset_dir, 'task_events', f),
                                     header=None, index_col=False,
                                     compression='gzip',
                                     names=task_events_schema)

        for event in task_events_df.itertuples():
            yield event
