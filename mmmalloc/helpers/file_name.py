# -*- coding: utf-8 -*-

from os import path


class FileName(object):
    def __init__(self, *args, **kwargs):
        self.name = None
        self.attributes = None
        getattr(self, args[0])(*args[1:], **kwargs)

    def alloc(self, resource_type, scheduling_period, delta,
              resource_percentage):
        if self.name is None:
            self.name = 'alloc-%s-%s-%s-%s.csv' % (resource_type,
                                                   str(scheduling_period),
                                                   str(delta),
                                                   str(resource_percentage))
        self.attributes = {'resource_type': resource_type,
                           'scheduling_period': int(scheduling_period),
                           'delta': float(delta),
                           'resource_percentage': float(resource_percentage)}

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

    def wait_by_class(self, allocator, resource_percentage, *args,
                      **kwargs):
        extra_options = ['same_share', 'reserved', 'weighted']
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
            self.name = 'wait_by_class-%s-%s' % (allocator,
                                                 str(resource_percentage))
            for opt in extra_options:
                if extra_options_dict[opt]:
                    self.name += '-' + opt
            self.name += '.json'

        self.attributes = {'allocator': allocator,
                           'resource_percentage': float(resource_percentage)}
        self.attributes.update(extra_options_dict)

    def completion_ratio(self, allocator, resource_percentage, delta=0,
                         *args, **kwargs):
        extra_options = ['same_share', 'reserved', 'weighted']
        extra_options_dict = {k: False for k in extra_options}

        for key in kwargs.copy():
            if key not in extra_options:
                del kwargs[key]

        extra_options_dict.update(kwargs)

        for arg in args:
            if arg not in extra_options:
                raise AttributeError(arg)
            extra_options_dict[arg] = True

        if self.name is None:
            self.name = 'completion_ratio-%s-%s-%s' % (
                allocator, str(resource_percentage), str(delta))
            for opt in extra_options:
                if extra_options_dict[opt]:
                    self.name += '-' + opt
            self.name += '.json'

        self.attributes = {'allocator': allocator,
                           'resource_percentage': float(resource_percentage),
                           'delta': float(delta)}
        self.attributes.update(extra_options_dict)

    def credibility(self, resource_type, scheduling_period, delta,
                    resource_percentage):
        if self.name is None:
            self.name = 'credibility-%s-%s-%s-%s.csv' % (
                resource_type, str(scheduling_period), str(delta),
                str(resource_percentage))
        self.attributes = {'resource_type': resource_type,
                           'scheduling_period': int(scheduling_period),
                           'delta': float(delta),
                           'resource_percentage': float(resource_percentage)}

    def user_needs(self, resource_type, scheduling_period, num_users):
        if self.name is None:
            self.name = 'user_needs-%s-%s-%s.csv' % (resource_type,
                                                     str(scheduling_period),
                                                     str(num_users))
        self.attributes = {'resource_type': resource_type,
                           'scheduling_period': int(scheduling_period),
                           'num_users': int(num_users)}

    def __getattr__(self, name):
        if name[-4:] != '.csv':
            if name not in self.attributes:
                raise AttributeError(name)
            return self.attributes[name]
        self.name = name
        name = path.basename(name)
        params_lists = name[:-4].split('-')
        if params_lists[0] not in dir(FileName):
            raise AttributeError(params_lists[0])
        getattr(self, params_lists[0])(*params_lists[1:])
        return lambda: None
