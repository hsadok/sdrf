import os
from pandas import read_csv


class Schema:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def __getattr__(self, name):
        sub_directories = next(os.walk(self.dataset_path))[1]
        if name not in sub_directories:
            raise AttributeError
        schema = read_csv(os.path.join(self.dataset_path, 'schema.csv'))
        file_pattern_select = schema[schema['file pattern'].str.contains(name)]
        file_pattern_content = file_pattern_select['content'].tolist()
        return file_pattern_content
