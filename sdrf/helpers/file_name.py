# -*- coding: utf-8 -*-

from os import path


class FileName(object):
    def __init__(self, *args, **kwargs):
        self.name = None
        self.attributes = None
        getattr(self, args[0])(*args[1:], **kwargs)

    def task_sim(self, allocator, resource_percentage, delta=0,
                 *args, **kwargs):
        extra_options = ['same_share', 'reserved', 'weighted', 'jobs', 'wait']
        extra_options_dict = {k: False for k in extra_options}

        for key in kwargs:
            if key not in extra_options:
                raise AttributeError(key)

        extra_options_dict.update(kwargs)

        for arg in args:
            if arg not in extra_options:
                raise AttributeError(arg)
            extra_options_dict[arg] = True

        if self.name is None:
            self.name = 'task_sim-%s-%s-%s' % (allocator,
                                               str(resource_percentage),
                                               str(delta))
            for opt in extra_options:
                if extra_options_dict[opt]:
                    self.name += '-' + opt

            self.name += '.csv'

        self.attributes = {'allocator': allocator,
                           'resource_percentage': float(resource_percentage),
                           'delta': float(delta)}
        self.attributes.update(extra_options_dict)

    def __getattr__(self, name):
        if not name.endswith('.csv') and not name.endswith('.json'):
            if name not in self.attributes:
                raise AttributeError(name)
            return self.attributes[name]
        self.name = name
        name = path.basename(name)
        name = '.'.join(name.split('.')[:-1])
        params_lists = name.split('-')
        if params_lists[0] not in dir(FileName):
            raise AttributeError(params_lists[0])
        getattr(self, params_lists[0])(*params_lists[1:])
        return lambda: None
