# -*- coding: utf-8 -*-
import heapq


class PriorityQueue(object):
    def __init__(self, initial=None):
        self.finder = {}
        if initial is None:
            self.heap = []
        else:
            self.heap = [[p, i] for i, p in enumerate(initial)]
            for i in self.heap:
                self.finder[i[1]] = i
            heapq.heapify(self.heap)
        self.removed_name = '__REMOVED__'

    def add(self, name, priority):
        if name in self.finder:
            if priority == self.finder[name][0]:
                return
            self.remove(name)
        entry = [priority, name]
        self.finder[name] = entry
        heapq.heappush(self.heap, entry)

    def pop(self):
        while self.heap:
            priority, name = heapq.heappop(self.heap)
            if name != self.removed_name:
                del self.finder[name]
                return name
        return None

    def get_min(self):
        while self.heap:
            priority, name = self.heap[0]
            if name == self.removed_name:
                heapq.heappop(self.heap)
            else:
                return name
        return None

    def sorted_elements(self):
        def elements_iterator():
            min_element = self.get_min()  # try not to sort at first

            if min_element is None:
                return

            yield min_element

            self.heap.sort()
            for i in self.heap[1:]:
                name = i[1]
                if name != self.removed_name:
                    yield i

        return elements_iterator()

    def remove(self, name):
        entry = self.finder[name]
        entry[1] = self.removed_name
