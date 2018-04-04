import json
from os.path import dirname, realpath, join
import ctypes as ct

lib_dir = dirname(realpath(__file__))
lib_path = join(lib_dir, 'c_dynamic_priority_queue', 'lib_c_priority_queue.so')
lib = ct.cdll.LoadLibrary(lib_path)

lib.PriorityQueue_new.restype = ct.c_void_p
lib.PriorityQueue_pop.restype = ct.c_void_p
lib.PriorityQueue_get_min.restype = ct.c_void_p
lib.PriorityQueue_remove.restype = ct.c_void_p
lib.PriorityQueue_cbegin.restype = ct.c_void_p
lib.PriorityQueue_get_element_from_it.restype = ct.c_void_p
lib.LiveTree_new.restype = ct.c_void_p
lib.LiveTree_pop.restype = ct.c_void_p
lib.LiveTree_get_min.restype = ct.c_void_p
lib.LiveTree_remove.restype = ct.c_void_p
lib.LiveTree_cbegin.restype = ct.c_void_p
lib.LiveTree_get_element_from_it.restype = ct.c_void_p
lib.Element_new.restype = ct.c_void_p
lib.Element_get_cpu_credibility.restype = ct.c_double
lib.Element_get_memory_credibility.restype = ct.c_double
lib.Element_get_cpu_relative_allocation.restype = ct.c_double
lib.Element_get_memory_relative_allocation.restype = ct.c_double
lib.Element_get_priority.restype = ct.c_double
lib.Element_get_update_time.restype = ct.c_double


max_repr_size = 10000


class PriorityQueueIterator:
    def __init__(self, queue_ptr):
        self.queue_ptr = queue_ptr
        self.iter_ptr = ct.c_void_p(lib.PriorityQueue_cbegin(self.queue_ptr))

    def __del__(self):
        lib.PriorityQueue_delete_it(self.iter_ptr)

    def __iter__(self):
        return self

    def next(self):
        if lib.PriorityQueue_it_is_end(self.queue_ptr, self.iter_ptr):
            raise StopIteration

        element_ptr = ct.c_void_p(lib.PriorityQueue_get_element_from_it(self.iter_ptr))
        lib.PriorityQueue_it_next(self.iter_ptr)
        return Element(obj=element_ptr)


class PriorityQueue(object):
    def __init__(self):
        self.obj = ct.c_void_p(lib.PriorityQueue_new())

    def __del__(self):
        lib.PriorityQueue_delete(self.obj)

    def __repr__(self):
        buf = ct.create_string_buffer(max_repr_size)
        lib.PriorityQueue_string(self.obj, buf, max_repr_size)
        return buf.value

    def __contains__(self, key):
        return bool(lib.PriorityQueue_element_is_in(self.obj, key))

    def add(self, element):
        lib.PriorityQueue_add(self.obj, element.obj)

    def pop(self, current_time):
        element_obj = ct.c_void_p(lib.PriorityQueue_pop(self.obj,ct.c_double(current_time)))
        return Element(obj=element_obj)

    def get_min(self, current_time):
        element_obj = ct.c_void_p(lib.PriorityQueue_get_min(self.obj,
                                                ct.c_double(current_time)))
        return Element(obj=element_obj)

    def remove(self, name):
        element_obj = ct.c_void_p(lib.PriorityQueue_remove(self.obj, name))
        return Element(obj=element_obj)

    def is_empty(self):
        return bool(lib.PriorityQueue_empty(self.obj))

    def update(self, current_time):
        lib.PriorityQueue_update(self.obj, ct.c_double(current_time))

    def sorted_elements(self):
        return PriorityQueueIterator(self.obj)

    @staticmethod
    def print_stats(file_name, info=None):
        if info is not None:
            info['queue'] = 'PriorityQueue'
            info_string = json.dumps(info)
        else:
            info_string = ''
        c_info = ct.c_char_p(info_string)
        c_file_name = ct.c_char_p(file_name)
        lib.PriorityQueue_print_stats(c_info, c_file_name)


class LiveTreeIterator:
    def __init__(self, queue_ptr):
        self.queue_ptr = queue_ptr
        self.iter_ptr = ct.c_void_p(lib.LiveTree_cbegin(self.queue_ptr))

    def __del__(self):
        lib.LiveTree_delete_it(self.iter_ptr)

    def __iter__(self):
        return self

    def next(self):
        if lib.LiveTree_it_is_end(self.queue_ptr, self.iter_ptr):
            raise StopIteration

        element_ptr = ct.c_void_p(lib.LiveTree_get_element_from_it(
            self.iter_ptr))
        lib.LiveTree_it_next(self.iter_ptr)
        return Element(obj=element_ptr)


class LiveTree(object):
    def __init__(self):
        self.obj = ct.c_void_p(lib.LiveTree_new())

    def __del__(self):
        lib.LiveTree_delete(self.obj)

    def __repr__(self):
        buf = ct.create_string_buffer(max_repr_size)
        lib.LiveTree_string(self.obj, buf, max_repr_size)
        return buf.value

    def __contains__(self, key):
        return bool(lib.LiveTree_element_is_in(self.obj, key))

    def add(self, element):
        lib.LiveTree_add(self.obj, element.obj)

    def pop(self, current_time):
        element_obj = ct.c_void_p(lib.LiveTree_pop(self.obj,
                                                   ct.c_double(current_time)))
        return Element(obj=element_obj)

    def get_min(self, current_time):
        element_obj = ct.c_void_p(lib.LiveTree_get_min(
            self.obj, ct.c_double(current_time)))
        return Element(obj=element_obj)

    def remove(self, name):
        element_obj = ct.c_void_p(lib.LiveTree_remove(self.obj, name))
        return Element(obj=element_obj)

    def is_empty(self):
        return bool(lib.LiveTree_empty(self.obj))

    def update(self, current_time):
        lib.LiveTree_update(self.obj, ct.c_double(current_time))

    def sorted_elements(self):
        return LiveTreeIterator(self.obj)

    @staticmethod
    def print_stats(file_name, info=None):
        if info is not None:
            info['queue'] = 'LiveTree'
            info_string = json.dumps(info)
        else:
            info_string = ''
        c_info = ct.c_char_p(info_string)
        c_file_name = ct.c_char_p(file_name)
        lib.LiveTree_print_stats(c_info, c_file_name)


class Element(object):
    def __init__(self, name=None, update_time=None, tau=None, system_cpu=None,
                 cpu_credibility=None, cpu_relative_allocation=None,
                 cpu_share=None, system_memory=None, memory_credibility=None,
                 memory_relative_allocation=None, memory_share=None, obj=None):
        if obj is None:
            self.obj = ct.c_void_p(lib.Element_new(
                name, ct.c_double(update_time), ct.c_double(tau),
                ct.c_double(system_cpu), ct.c_double(cpu_credibility),
                ct.c_double(cpu_relative_allocation), ct.c_double(cpu_share),
                ct.c_double(system_memory), ct.c_double(memory_credibility),
                ct.c_double(memory_relative_allocation),
                ct.c_double(memory_share))
            )
        else:
            self.obj = obj

    def __del__(self):
        lib.Element_delete(self.obj)

    def __repr__(self):
        buf = ct.create_string_buffer(max_repr_size)
        lib.Element_string(self.obj, buf, max_repr_size)
        return buf.value

    def __hash__(self):
        hash(self.name)

    def update(self, current_time):
        lib.Element_update(self.obj, ct.c_double(current_time))

    @property
    def name(self):
        return lib.Element_get_name(self.obj)

    @property
    def cpu_credibility(self):
        return ct.c_double(lib.Element_get_cpu_credibility(self.obj))

    @property
    def memory_credibility(self):
        return ct.c_double(lib.Element_get_memory_credibility(self.obj))

    @property
    def priority(self):
        return ct.c_double(lib.Element_get_priority(self.obj))

    @property
    def update_time(self):
        return ct.c_double(lib.Element_get_update_time(self.obj))

    @property
    def cpu_relative_allocation(self):
        return ct.c_double(lib.Element_get_cpu_relative_allocation(self.obj))

    @property
    def memory_relative_allocation(self):
        return ct.c_double(lib.Element_get_memory_relative_allocation(self.obj))

    @cpu_relative_allocation.setter
    def cpu_relative_allocation(self, value):
        lib.Element_set_cpu_relative_allocation(self.obj, ct.c_double(value))

    @memory_relative_allocation.setter
    def memory_relative_allocation(self, value):
        lib.Element_set_memory_relative_allocation(self.obj, ct.c_double(value))
