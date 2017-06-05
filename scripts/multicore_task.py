# import sys
# sys.path.insert(0, '/home/gta/Dropbox/estudos/UFRJ/GTA/pesquisas')
from jug import Task
import sys
from mmmalloc.simulators.simulate_task_allocation import wdrf, mmm_drf

mean = [722.05833582, 631.427965593]
num_users = 633

tasks_file = sys.argv[1]

for i in xrange(1, 21):
    resource_percentage = i/10.0
    resource = [mean[0]*resource_percentage, mean[1]*resource_percentage]
    users_resources = [resource[0]/num_users, resource[1]/num_users]
    users_resources = [users_resources] * num_users
    Task(mmm_drf,
         resource, users_resources, resource_percentage, '.', tasks_file)
    # Task(wdrf, resource, resource_percentage, '.', tasks_file, [1] * 1000)
    # wdrf(resource, resource_percentage, '.', tasks_file, [1] * 1000)
