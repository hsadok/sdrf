# -*- coding: utf-8 -*-
from sortedcontainers import SortedList


class PriorityQueue(object):
    def __init__(self, initial=None):
        self.finder = {}
        if initial is None:
            self.heap = SortedList()
        else:
            self.heap = SortedList([p, i] for i, p in enumerate(initial))
            for i in self.heap:
                self.finder[i[1]] = i
        self.pending_removal = []
        self.removed_name = '__REMOVED__'

    def add(self, name, priority):
        self.cleanup_pending_removal()

        if name in self.finder:
            if priority == self.finder[name][0]:
                return
            self.remove(name)
        entry = [priority, name]
        self.finder[name] = entry
        self.heap.add(entry)

    def pop(self, get_priority=False):
        self.cleanup_pending_removal()

        while self.heap:
            priority, name = self.heap.pop(0)
            if name != self.removed_name:
                del self.finder[name]
                if get_priority:
                    return name, priority
                return name
        return None

    def get_min(self, get_priority=False):
        while self.heap:
            priority, name = self.heap[0]
            if name == self.removed_name:
                del self.heap[0]
            else:
                if get_priority:
                    return name, priority
                return name
        return None

    def sorted_elements(self, get_priority=False):
        self.cleanup_pending_removal()

        def elements_iterator():
            for index, (priority, name) in enumerate(self.heap):
                if name != self.removed_name:
                    if get_priority:
                        yield name, priority
                    else:
                        yield name
                else:
                    self.pending_removal.append(index)

        return elements_iterator()

    def remove(self, name):
        entry = self.finder.pop(name)
        entry[1] = self.removed_name

    def cleanup_pending_removal(self):
        for index in reversed(self.pending_removal):
            del self.heap[index]
        self.pending_removal = []
