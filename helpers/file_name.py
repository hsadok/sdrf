# -*- coding: utf-8 -*-

from os import path


class FileName(object):
    def __init__(self, *args):
        self.name = None
        self.attributes = None
        getattr(self, args[0])(*args[1:])

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
