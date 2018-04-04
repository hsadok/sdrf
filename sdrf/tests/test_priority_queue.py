from math import log

from sdrf.helpers.live_tree import PriorityQueue, Element

system_cpu = 20.0
system_memory = 100.0
delta = 0.9999
tau = -1/log(delta)

update_time = 1.0

queue = PriorityQueue()

c_o_cpu = -8.0
c_o_mem = 1.0
o_cpu = 5.0
o_mem = 5.0
e1 = Element(10, update_time, tau, system_cpu, c_o_cpu, o_cpu, system_memory,
             c_o_mem, o_mem)
queue.add(e1)

queue.get_min(1)

print queue
c_o_cpu = -8.0
c_o_mem = 3.3
o_cpu = 0.0
o_mem = 3.3
e2 = Element(5, update_time, tau, system_cpu, c_o_cpu, o_cpu, system_memory,
             c_o_mem, o_mem)
queue.add(e2)
print queue

update_time = 7816
queue.update(update_time)
print queue

print 'min:', queue.get_min(update_time)
print 'min:', queue.pop(update_time)
print 'min:', queue.pop(update_time)
print queue

c_o_cpu = -8.0
c_o_mem = 1.0
o_cpu = 5.0
o_mem = 5.0
e3 = Element(10, update_time, tau, system_cpu, c_o_cpu, o_cpu, system_memory,
             c_o_mem, o_mem)
queue.add(e3)
queue.add(e2)
print queue

update_time += 2000
queue.update(update_time)
print queue

update_time += 2000
queue.update(update_time)
print queue

update_time += 2000
queue.update(update_time)
print queue

update_time += 2000
queue.update(update_time)
print queue

print 'remove'

queue.remove(10)
print queue

queue.add(e3)
print queue
