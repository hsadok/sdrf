import click
from psutil import cpu_count
from subprocess import call
import time


@click.command()
@click.argument('command')
def main(command):
    call(['tmux', 'new', '-s', 'credibility allocation', '-d'])

    for _ in xrange(cpu_count()/2):
        call(['tmux', 'new-window', command])
        time.sleep(60)
    # ' jug execute code/scripts/multicore_task.py data/filtered_tasks.csv'

if __name__ == '__main__':
    main()
