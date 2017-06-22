from os.path import dirname, realpath, join
import ctypes as ct

lib_path = join(dirname(realpath(__file__)), 'lib_c_priority_queue.so')
lib = ct.cdll.LoadLibrary(lib_path)

lib.PriorityQueue_new.restype = ct.c_void_p
lib.PriorityQueue_pop.restype = ct.c_void_p
lib.PriorityQueue_get_min.restype = ct.c_void_p
lib.PriorityQueue_cbegin.restype = ct.c_void_p
lib.PriorityQueue_get_element_from_it.restype = ct.c_void_p
lib.DynamicPriorityQueue_new.restype = ct.c_void_p
lib.DynamicPriorityQueue_pop.restype = ct.c_void_p
lib.DynamicPriorityQueue_get_min.restype = ct.c_void_p
lib.DynamicPriorityQueue_cbegin.restype = ct.c_void_p
lib.DynamicPriorityQueue_get_element_from_it.restype = ct.c_void_p
lib.Element_new.restype = ct.c_void_p
lib.Element_get_priority.restype = ct.c_double
lib.Element_get_update_time.restype = ct.c_double

max_repr_size = 10000


class PriorityQueue(object):
    def __init__(self):
        self.obj = lib.PriorityQueue_new()

    def __del__(self):
        lib.PriorityQueue_delete(self.obj)

    def __repr__(self):
        buf = ct.create_string_buffer(max_repr_size)
        lib.PriorityQueue_string(self.obj, buf, max_repr_size)
        return buf.value

    def add(self, element):
        lib.PriorityQueue_add(self.obj, element.obj)

    def pop(self, current_time):
        element_obj = lib.PriorityQueue_pop(self.obj,ct.c_double(current_time))
        return Element(obj=element_obj)

    def get_min(self, current_time):
        element_obj = lib.PriorityQueue_get_min(self.obj,
                                                ct.c_double(current_time))
        return Element(obj=element_obj)

    def remove(self, name):
        lib.PriorityQueue_remove(self.obj, name)

    def is_empty(self):
        return bool(lib.PriorityQueue_empty(self.obj))

    def update(self, current_time):
        lib.PriorityQueue_update(self.obj, ct.c_double(current_time))

    def sorted_elements(self):
        def elements_iterator():
            it = lib.PriorityQueue_cbegin(self.obj)
            while not lib.PriorityQueue_it_is_end(self.obj, it):
                element_obj = lib.PriorityQueue_get_element_from_it(it)
                yield Element(obj=element_obj)
                lib.PriorityQueue_it_next(it)

            lib.PriorityQueue_delete_it(it)

        return elements_iterator()


class DynamicPriorityQueue(object):
    def __init__(self):
        self.obj = lib.DynamicPriorityQueue_new()

    def __del__(self):
        lib.DynamicPriorityQueue_delete(self.obj)

    def __repr__(self):
        buf = ct.create_string_buffer(max_repr_size)
        lib.DynamicPriorityQueue_string(self.obj, buf, max_repr_size)
        return buf.value

    def add(self, element):
        lib.DynamicPriorityQueue_add(self.obj, element.obj)

    def pop(self, current_time):
        element_obj = lib.DynamicPriorityQueue_pop(self.obj,
                                                   ct.c_double(current_time))
        return Element(obj=element_obj)

    def get_min(self, current_time):
        element_obj = lib.DynamicPriorityQueue_get_min(
            self.obj, ct.c_double(current_time))
        return Element(obj=element_obj)

    def remove(self, name):
        lib.DynamicPriorityQueue_remove(self.obj, name)

    def is_empty(self):
        return bool(lib.DynamicPriorityQueue_empty(self.obj))

    def update(self, current_time):
        lib.DynamicPriorityQueue_update(self.obj, ct.c_double(current_time))

    def sorted_elements(self):
        def elements_iterator():
            it = lib.DynamicPriorityQueue_cbegin(self.obj)
            while not lib.DynamicPriorityQueue_it_is_end(self.obj, it):
                element_obj = lib.DynamicPriorityQueue_get_element_from_it(it)
                yield Element(obj=element_obj)
                lib.DynamicPriorityQueue_it_next(it)

            lib.DynamicPriorityQueue_delete_it(it)

        return elements_iterator()


class Element(object):
    def __init__(self, name=None, update_time=None, tau=None, system_cpu=None,
                 cpu_credibility=None, cpu_relative_allocation=None,
                 system_memory=None, memory_credibility=None,
                 memory_relative_allocation=None, obj=None):
        if obj is None:
            self.obj = lib.Element_new(name,
                                       ct.c_double(update_time),
                                       ct.c_double(tau),
                                       ct.c_double(system_cpu),
                                       ct.c_double(cpu_credibility),
                                       ct.c_double(cpu_relative_allocation),
                                       ct.c_double(system_memory),
                                       ct.c_double(memory_credibility),
                                       ct.c_double(memory_relative_allocation))
        else:
            self.obj = obj

    def __del__(self):
        lib.Element_delete(self.obj)

    def __repr__(self):
        buf = ct.create_string_buffer(max_repr_size)
        lib.Element_string(self.obj, buf, max_repr_size)
        return buf.value

    @property
    def priority(self):
        return lib.Element_get_priority(self.obj)

    @property
    def update_time(self):
        return lib.Element_get_update_time(self.obj)
