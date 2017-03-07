# -*- coding: utf-8 -*-

from collections import defaultdict
from os import listdir, path

from helpers.file_name import FileName


class Allocation(object):
    def __init__(self, data_path):
        files = sorted(listdir(data_path))
        files = filter(lambda x: x[-4:] == '.csv', files)
        alloc_files = filter(lambda x: x.startswith('alloc'), files)

        user_needs_files = filter(lambda x: x.startswith('user_needs'), files)
        user_needs_files = map(FileName, user_needs_files)
        user_needs_files = {n.attributes['resource_type']: path.join(
            data_path, n.name) for n in user_needs_files}
        self._allocations = defaultdict(list)
        for f in alloc_files:
            file_name = FileName(f)
            params_dict = file_name.attributes
            resource_type = params_dict['resource_type']
            params_dict['file_name'] = path.join(data_path, f)
            params_dict['types_file_name'] = user_needs_files[resource_type]
            self._allocations[resource_type].append(params_dict)
        self.user_type_files = user_needs_files

    def resource_types(self):
        return self._allocations.keys()

    def __getattr__(self, name):
        return self._allocations[name]

    def iteritems(self):
        return self._allocations.iteritems()
