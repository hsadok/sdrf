from math import log

from c_priority_queue import DynamicPriorityQueue, Element

dpq = DynamicPriorityQueue()
update_time = 1.0
system_cpu = 20.0
system_memory = 100.0
delta = 0.9999
tau = -1/log(delta)
c_o_cpu = -8.0
c_o_mem = 1.0
o_cpu = 5.0
o_mem = 5.0
e1 = Element(10, update_time, tau, system_cpu, c_o_cpu, o_cpu,
             system_memory, c_o_mem, o_mem)
dpq.add(e1)
print dpq.get_min(1)
